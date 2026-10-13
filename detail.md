# MASTER ARCHITECTURAL & SYSTEM IMPLEMENTATION SPECIFICATION
## Dual-View Anthropometric Computer Vision, Intelligent Fit Kinematics, Photometric Color Profiling, and Conversational Retrieval-Augmented Generation (RAG) Microservice

**Author & Systems Architect:** Senior Principal ML Architect & Professor of Applied Computational Vision (30-Year Veteran in Production AI Systems & Statistical Pattern Recognition)  
**Document Reference:** `detail.md`  
**System Target:** Enterprise E-Commerce Automated Fit, Sizing & Styling Recommendation Engine  
**Runtime Environment:** Python 3.11/3.13, CPU-Optimized High-Throughput Asynchronous Architecture (`FastAPI` + `scikit-learn` + `OpenCV` + `ChromaDB` / `Google Gemini`)

---

## 1. Executive Summary & Architectural Thesis

In modern algorithmic apparel sizing and e-commerce computer vision, the fundamental objective is to eliminate return rates (which historically range between 25% and 40% in digital apparel retail) while preserving frictionless user onboarding. Traditional 3D body scanners (e.g., structured-light booths, dense LiDAR point clouds) provide millimeter precision but are commercially impractical for consumer mobile devices.

This project implements an end-to-end, multi-model production pipeline that translates **uncalibrated dual-view 2D binary silhouettes** (Frontal view $I_{\text{front}}$ and Lateral profile $I_{\text{side}}$) along with sparse physical metadata (User Height $h \text{ (cm)}$, Mass $w \text{ (kg)}$, Gender $g$) into **true 3D anthropometric circumferences** (Chest, Waist, Hip, etc.). 

Around this core anthropometric regression engine, we build:
1. **Model 1: Calibrated Anthropometric Regressor:** Dual-contour geometric slicing + Ramanujan elliptic integral approximation + Regularized Ridge/RandomForest Regression.
2. **Model 2: Garment Fit & Kinematic Ease Classifier:** Ease-allowance computation $\Delta = G_{\text{spec}} - M_{\text{body}}$ mapped through parametric tolerance bands to predict fit polarity (`Small`, `Fit`, `Large`).
3. **Model 3: Photometric CIELAB Skin-Tone & Color Palette Matcher:** Illumination-invariant Euclidean clustering in CIE $L^*a^*b^*$ color space coupled with Individual Typology Angle ($\text{ITA}^\circ$) seasonal classification.
4. **Model 4: Modular Retrieval-Augmented Generation (RAG) Advisory Chatbot:** Hexagonal / Ports-and-Adapters architecture decoupling the Vector Store (`ChromaDB` / Local Cosine Reranker) and LLM inference engine (`Google Gemini API` / Offline Fallback).

---

## 2. Directory Structure & Architecture Transformation

To comply with high-availability Clean Architecture (Dependency Inversion, Single Responsibility, Separation of Concerns), the codebase transitions from a flat raw dataset repository into the following enterprise layout:

```text
c:/Users/ADMIN/Desktop/model/
├── IMPLEMENTATION_PLAN.md             # High-level strategic overview
├── detail.md                          # Master architectural specification (this document)
├── requirements.txt                   # Production & development dependencies
├── .env.example                       # Environment template (API keys, ports, debug flags)
│
├── core/                              # Hexagonal Core / Domain Abstractions
│   ├── __init__.py
│   ├── config.py                      # Pydantic BaseSettings with typed environment parsing
│   ├── exceptions.py                  # Domain-specific hierarchy of exceptions & HTTP mappers
│   └── interfaces/                    # Abstract Base Classes (ABCs)
│       ├── __init__.py
│       ├── llm_provider.py            # Abstract Base LLM interface (Gemini / OpenAI / Mock)
│       └── vector_store.py            # Abstract Vector Database interface (Chroma / In-Memory)
│
├── models/                            # Model Inference Engines & Serialized Artifacts
│   ├── __init__.py
│   ├── measurement/                   # Model 1: Anthropometric Estimation
│   │   ├── __init__.py
│   │   ├── feature_extractor.py       # Geometric contour slicing & calibration mathematics
│   │   ├── regressor.py               # Serialized pipeline loader & inference wrapper
│   │   └── artifacts/                 # Serialized weights (body_regressor.pkl, scaler.pkl, metadata.json)
│   ├── fit/                           # Model 2: Garment Fit Recommendation
│   │   ├── __init__.py
│   │   └── fit_engine.py              # Parametric ease kinematics & classifier
│   └── color/                         # Model 3: Photometric Color Matcher
│       ├── __init__.py
│       └── color_engine.py            # CIE Lab conversion, K-Means clustering, ITA classifier
│
├── services/                          # External Infrastructure Adapters
│   ├── __init__.py
│   ├── gemini_llm.py                  # Google Gemini API adapter implementing LLMProvider
│   ├── vector_db.py                   # ChromaDB & In-Memory Fallback adapter implementing VectorStore
│   └── rag_service.py                 # RAG orchestrator (Chunking, Embedding, Context Injection)
│
├── data/                              # Data Pipeline & Ingestion Scripts
│   ├── __init__.py
│   ├── train_pipeline.py              # Model 1 training, hyperparameter search, and export script
│   ├── evaluate.py                    # Independent validation script against testB/testA
│   ├── docs/                          # Knowledge base markdown documents for RAG ingestion
│   │   ├── apparel_care.md
│   │   ├── return_policy.md
│   │   └── sizing_guidelines.md
│   └── raw/                           # Raw BodyM datasets
│       ├── train/                     # Training split (hwg_metadata, measurements, mask, mask_left)
│       ├── testA/                     # Test split A
│       └── testB/                     # Test split B (Benchmarking ground truth)
│
├── app/                               # FastAPI Presentation Layer
│   ├── __init__.py
│   ├── main.py                        # FastAPI entry point, CORS, lifespan startup/shutdown
│   ├── dependencies.py                # Dependency Injection graph
│   ├── schemas/                       # Pydantic v2 Request/Response Data Transfer Objects (DTOs)
│   │   ├── __init__.py
│   │   ├── measurement.py             # Fit-check & measurement schemas
│   │   ├── fit.py                     # Sizing recommendation schemas
│   │   ├── color.py                   # Skin tone & palette schemas
│   │   └── chatbot.py                 # Query, context, and LLM response schemas
│   └── routers/                       # HTTP API Routes
│       ├── __init__.py
│       ├── fit_check.py               # POST /api/v1/fit-check
│       ├── recommend.py               # POST /api/v1/recommend
│       ├── color.py                   # POST /api/v1/color-palette
│       ├── chatbot.py                 # POST /api/v1/chat
│       └── health.py                  # GET /health, GET /metrics
│
└── tests/                             # Comprehensive Automated Test Harness
    ├── __init__.py
    ├── test_geometry.py               # Unit tests for contour slicing & Ramanujan approximations
    ├── test_regressor.py              # Unit tests for Model 1 predictions & MAE bounds
    ├── test_fit.py                    # Unit tests for Model 2 ease bounds
    ├── test_color.py                  # Unit tests for Model 3 CIE Lab clustering
    ├── test_rag.py                    # Unit tests for vector search and RAG synthesis
    └── test_api.py                    # End-to-end integration tests for all FastAPI endpoints
```

---

## 3. The 10-Phase Master Execution Blueprint

We will execute this transformation through **exactly 10 sequential, rigorous phases**. Below is the exhaustive engineering specification for every phase.

---

### PHASE 1: Deep Exploratory Data Analysis (EDA) & Data Ingestion Pipeline

#### 1. Scope & Objective
Establish a clean, deterministic ingestion pipeline for the BodyM dataset across `train/train`, `testB/testB`, and `testA/testA`. Map the associative relations between:
- Subject demographics: `hwg_metadata.csv` (`subject_id`, `gender`, `height_cm`, `weight_kg`).
- Ground-truth 3D anthropometry: `measurements.csv` (14 anatomical targets: `chest`, `waist`, `hip`, `ankle`, `arm-length`, `bicep`, `calf`, `forearm`, `height`, `leg-length`, `shoulder-breadth`, `shoulder-to-crotch`, `thigh`, `wrist`).
- Photo identifier index: `subject_to_photo_map.csv` (`subject_id`, `photo_id`).
- Binary silhouettes: Frontal view in `mask/{photo_id}.png` and Left Lateral profile in `mask_left/{photo_id}.png`.

#### 2. Technical Pitfalls & Mathematical Challenges
- **One-to-Many Subject-to-Photo Mappings:** A single `subject_id` frequently associates with multiple `photo_id` instances (representing multiple poses or garment variations). Naive merging produces data leakage and skewed loss functions. We must establish a canonical image pairing policy or average extracted geometric features per subject.
- **Missing or Corrupted Masks:** Binary silhouettes may contain pixel holes, non-zero borders, or missing lateral pairs.
- **Non-Uniform Scaling & Inconsistent Aspect Ratios:** Image matrices are uncalibrated 2D projections.

#### 3. Algorithmic Changes & Engineering Solutions
- Construct `data/train_pipeline.py` with an ingestion module `BodyMDatasetLoader`.
- Inner-join `hwg_metadata.csv` with `measurements.csv` on `subject_id`.
- Implement verification checks: Verify that for every `(subject_id, photo_id)`, both `mask/{photo_id}.png` and `mask_left/{photo_id}.png` exist on the filesystem. Filter orphaned entries cleanly with structured logging.

---

### PHASE 2: Computer Vision Silhouette Geometry & Mathematical Feature Engineering

#### 1. Scope & Objective
Transform raw 2D pixel masks into calibrated metric anatomical cross-sections without requiring heavy deep neural networks during CPU inference.

#### 2. Mathematical Formulations & Derivations

##### A. Bounding Box Metric Calibration
Let $M_{\text{front}}(x, y) \in \{0, 255\}$ and $M_{\text{side}}(x, y) \in \{0, 255\}$ denote the binary silhouettes.
We locate the human subject contour $C = \{(x_i, y_i)\}$.
The extreme vertical coordinates are:
$$y_{\text{vertex}} = \min_{y} \{ (x, y) \in C \}, \quad y_{\text{sole}} = \max_{y} \{ (x, y) \in C \}$$
The pixel stature is:
$$H_{\text{pixels}} = y_{\text{sole}} - y_{\text{vertex}}$$
Given the subject's true stature $h_{\text{cm}}$, the pixel-to-metric scaling factor $s$ is:
$$s = \frac{h_{\text{cm}}}{H_{\text{pixels}}} \quad (\text{cm / pixel})$$

##### B. Anatomical Cross-Section Slicing
Based on anthropometric anatomical standards (Winter's Human Biomechanics & Drillis & Contini proportional models):
- **Shoulder Level:** $y_{\text{shoulder}} = y_{\text{vertex}} + 0.18 \times H_{\text{pixels}}$
- **Chest / Bust Level:** $y_{\text{chest}} = y_{\text{vertex}} + 0.28 \times H_{\text{pixels}}$
- **Narrow Waist Level:** $y_{\text{waist}} = y_{\text{vertex}} + 0.42 \times H_{\text{pixels}}$
- **Trochanterion / Hip Level:** $y_{\text{hip}} = y_{\text{vertex}} + 0.53 \times H_{\text{pixels}}$
- **Thigh Mid-Level:** $y_{\text{thigh}} = y_{\text{vertex}} + 0.65 \times H_{\text{pixels}}$

At any given vertical coordinate $y_k$, the cross-sectional slice across the silhouette produces:
- Frontal Silhouette Width: $W_{\text{px}}(y_k) = \max \{x \mid M_{\text{front}}(x, y_k) = 255\} - \min \{x \mid M_{\text{front}}(x, y_k) = 255\}$
- Lateral Silhouette Depth: $D_{\text{px}}(y_k) = \max \{x \mid M_{\text{side}}(x, y_k) = 255\} - \min \{x \mid M_{\text{side}}(x, y_k) = 255\}$

Calibrated in centimeters:
$$W_{\text{cm}}(y_k) = W_{\text{px}}(y_k) \times s_{\text{front}}$$
$$D_{\text{cm}}(y_k) = D_{\text{px}}(y_k) \times s_{\text{side}}$$

##### C. Elliptic Circumference Estimation (Ramanujan's First Approximation)
Human torso cross-sections are topologically bounded by pseudo-ellipses with semi-major axis $a = \frac{W_{\text{cm}}}{2}$ and semi-minor axis $b = \frac{D_{\text{cm}}}{2}$.
The true circumference is given by the complete elliptic integral of the second kind:
$$C = 4a \int_{0}^{\pi/2} \sqrt{1 - e^2 \sin^2 \theta} \, d\theta, \quad e = \sqrt{1 - \frac{b^2}{a^2}}$$
To achieve sub-millisecond CPU execution, we utilize Ramanujan's high-precision approximation:
$$C_{\text{elliptic}} \approx \pi \left[ 3(a + b) - \sqrt{(3a + b)(a + 3b)} \right]$$
We compute pseudo-circumferences: $C_{\text{chest}}, C_{\text{waist}}, C_{\text{hip}}$.

##### D. Synthetic Feature Synthesis
To account for volumetric mass density, we engineer:
- Body Mass Index: $\text{BMI} = \frac{w_{\text{kg}}}{(h_{\text{cm}} / 100)^2}$
- Ponderal Index: $\text{PI} = \frac{w_{\text{kg}}}{(h_{\text{cm}} / 100)^3}$
- Binary Gender Encoding: $g \in \{0, 1\}$ (Female=0, Male=1)
- Aspect Ratios: $\frac{W_{\text{waist}}}{W_{\text{hip}}}$ (Waist-to-Hip Ratio proxy), $\frac{W_{\text{chest}}}{W_{\text{waist}}}$

**Final Engineered Feature Vector:**
$$X = \begin{bmatrix}
W_{\text{chest}}, D_{\text{chest}}, C_{\text{chest}}, \\
W_{\text{waist}}, D_{\text{waist}}, C_{\text{waist}}, \\
W_{\text{hip}}, D_{\text{hip}}, C_{\text{hip}}, \\
W_{\text{shoulder}}, W_{\text{thigh}}, \\
h_{\text{cm}}, w_{\text{kg}}, \text{BMI}, \text{PI}, g
\end{bmatrix} \in \mathbb{R}^{16}$$

#### 4. Project Structural Changes
- Create `models/measurement/feature_extractor.py`.
- Class `SilhouetteFeatureExtractor`:
  - Methods: `calibrate_scale(mask, height_cm)`, `extract_slice_widths(mask, levels)`, `compute_ramanujan_circumference(w, d)`, `extract_features(front_mask, side_mask, height_cm, weight_kg, gender)`.

---

### PHASE 3: Anthropometric Multi-Target Regression Formulation & Benchmark Training

#### 1. Scope & Objective
Formulate, train, and optimize the statistical learning pipeline mapping $X \in \mathbb{R}^{16} \to Y \in \mathbb{R}^{3}$ where $Y = [\text{chest}, \text{waist}, \text{hip}]^{\top}$.

#### 2. Mathematical Formulations & Loss Functions
We evaluate two complementary regression paradigms:

##### A. Regularized Ridge Regression (L2 Tikhonov Regularization)
Given the multicollinearity between $W, D, C, h, w$:
$$\min_{\mathbf{W}} \frac{1}{2N} \sum_{i=1}^N \| Y_i - \mathbf{W}^{\top} X_i \|_2^2 + \lambda \|\mathbf{W}\|_F^2$$
Analytical solution:
$$\mathbf{W}^* = (X^{\top} X + \lambda I)^{-1} X^{\top} Y$$
Guarantees global convexity, robust stability against collinear inputs, and instantaneous inference latency ($<0.1\text{ ms}$).

##### B. Random Forest Regressor & Gradient Boosting Ensembles
To capture non-linear morphological relationships (e.g., abdominal adipose accumulation curves as BMI exceeds $30\text{ kg/m}^2$):
$$\hat{Y}(X) = \frac{1}{B} \sum_{b=1}^B T_b(X)$$
Tuned with: `n_estimators=150`, `max_depth=12`, `min_samples_split=5`.

#### 3. Project Structural Changes
- Implement `data/train_pipeline.py`.
- Features cached to disk via Parquet or NumPy compressed arrays (`features_train.npz`) to allow rapid model iteration without recomputing image contour integrals.
- Pipeline exports production-ready artifacts to `models/measurement/artifacts/`:
  - `regressor_model.pkl` (Fitted Pipeline with `StandardScaler` + Regressor).
  - `feature_names.json`.
  - `metrics_train_val.json`.

---

### PHASE 4: Scientific Validation & Rigorous Error Analysis against TestB Benchmark

#### 1. Scope & Objective
Conduct an uncompromised evaluation against the held-out `testB/testB` split (which the model has never encountered during training or feature scaling).

#### 2. Evaluation Metrics & Statistical Bounds
We compute:
- **Mean Absolute Error (MAE):**
  $$\text{MAE}_k = \frac{1}{M} \sum_{j=1}^M | \hat{Y}_{j, k} - Y_{j, k} |$$
  *Acceptance Gate:* $\text{MAE}_{\text{chest}} \le 3.0\text{ cm}$, $\text{MAE}_{\text{waist}} \le 3.5\text{ cm}$, $\text{MAE}_{\text{hip}} \le 3.0\text{ cm}$.
- **Root Mean Squared Error (RMSE):**
  $$\text{RMSE}_k = \sqrt{\frac{1}{M} \sum_{j=1}^M (\hat{Y}_{j, k} - Y_{j, k})^2}$$
- **Coefficient of Determination ($R^2$ Score):**
  $$R^2 = 1 - \frac{\sum (Y - \hat{Y})^2}{\sum (Y - \bar{Y})^2}$$
  *Acceptance Gate:* $R^2 \ge 0.85$ across all major circumferences.

#### 3. Project Structural Changes
- Create `data/evaluate.py`:
  - Loads serialized `regressor_model.pkl`.
  - Ingests `testB/testB/hwg_metadata.csv` and `testB/testB/measurements.csv`.
  - Generates comprehensive tabular report and exports `evaluation_report_testB.json`.

---

### PHASE 5: Garment Fit & Kinematic Ease Recommendation Engine (Model 2)

#### 1. Scope & Objective
Implement Model 2 (`models/fit/fit_engine.py`) to provide precise apparel sizing recommendations (`Small`, `Fit`, `Large`) based on garment specification tolerances and human movement ease allowances.

#### 2. Mathematical Kinematics & Ease Allowance Formulation
In textile pattern making, **Garment Ease** is defined as the deliberate difference between the finished garment dimensions $G$ and the wearer's static anatomical body measurement $M_{\text{body}}$:
$$\text{Ease} = G_{\text{spec}} - M_{\text{body}}$$

##### Ease Classification Hierarchy:
1. **Dynamic Functional Ease:** Normal respiratory expansion and movement requires:
   - Chest: $+4\text{ cm}$ to $+7\text{ cm}$ ease for non-stretch woven fabrics; $+0\text{ cm}$ to $+3\text{ cm}$ for stretch knits.
   - Waist: $+2\text{ cm}$ to $+4\text{ cm}$.
   - Hip: $+4\text{ cm}$ to $+6\text{ cm}$.
2. **Tolerance Band Categorization:**
   Let $\delta_{\text{fabric}} \in [0, 1]$ represent fabric elastane stretch modulus.
   $$\text{Threshold}_{\text{tight}} = 0 - (4 \times \delta_{\text{fabric}})$$
   $$\text{Threshold}_{\text{loose}} = 6 + (2 \times (1 - \delta_{\text{fabric}}))$$
   - If $\text{Ease} < \text{Threshold}_{\text{tight}}$: Label = `Small` (Risk of constriction, seam tension failure).
   - If $\text{Threshold}_{\text{tight}} \le \text{Ease} \le \text{Threshold}_{\text{loose}}$: Label = `Fit` (Optimal drape and ergonomic comfort).
   - If $\text{Ease} > \text{Threshold}_{\text{loose}}$: Label = `Large` (Excess ease, baggy silhouette).

#### 3. Extensible Sizing Strategy
The engine accepts a garment size chart mapping (`XS`, `S`, `M`, `L`, `XL`, `XXL` with respective chest/waist/hip dimensions) and computes an ordinal compatibility score for every size, outputting the optimal recommended size alongside the fit classification.

---

### PHASE 6: Photometric CIELAB Skin-Tone & Color Palette Matcher (Model 3)

#### 1. Scope & Objective
Build an illumination-robust skin-tone profiler (`models/color/color_engine.py`) that analyzes facial/skin patches, projects them into a device-independent color space, clusters dominant dermal pigment tones, and maps them to harmonized seasonal color palettes.

#### 2. Mathematical Colorimetry in CIE $L^*a^*b^*$

##### A. Non-Linear RGB to CIELAB Transformation
Standard sRGB color spaces are non-perceptually uniform and highly vulnerable to shadow variations. The CIE $L^*a^*b^*$ space decouples luminance $L^*$ (lightness: 0=black, 100=white) from chromatic coordinates $a^*$ (green $\to$ red) and $b^*$ (blue $\to$ yellow).
The conversion follows:
1. Inverse sRGB gamma companding:
   $$C_{\text{linear}} = \begin{cases} \frac{C_{\text{srgb}}}{12.92} & C_{\text{srgb}} \le 0.04045 \\ \left(\frac{C_{\text{srgb}} + 0.055}{1.055}\right)^{2.4} & C_{\text{srgb}} > 0.04045 \end{cases}$$
2. CIE XYZ tristimulus conversion:
   $$\begin{bmatrix} X \\ Y \\ Z \end{bmatrix} = \mathbf{M} \begin{bmatrix} R_{\text{linear}} \\ G_{\text{linear}} \\ B_{\text{linear}} \end{bmatrix}$$
3. Mapping to $L^*, a^*, b^*$ relative to the D65 standard illuminant reference $(X_n, Y_n, Z_n)$.

##### B. Individual Typology Angle ($\text{ITA}^\circ$) & Melanin Classification
$$\text{ITA}^\circ = \frac{\arctan\left( \frac{L^* - 50}{b^*} \right) \times 180}{\pi}$$
- $\text{ITA} > 55^\circ$: Very Light / Fair
- $41^\circ < \text{ITA} \le 55^\circ$: Light
- $28^\circ < \text{ITA} \le 41^\circ$: Intermediate
- $10^\circ < \text{ITA} \le 28^\circ$: Tan / Olive
- $-30^\circ < \text{ITA} \le 10^\circ$: Brown
- $\text{ITA} \le -30^\circ$: Dark

##### C. Dominant Centroid Clustering (K-Means)
On extracted skin pixels, fit a $k=3$ K-Means cluster to separate specular glare and shadowing from true melanin/hemoglobin skin pigmentation. The primary cluster centroid in $a^*-b^*$ determines undertone:
- $\text{Undertone} = \text{Warm}$ if $b^* > 1.2 \times a^*$
- $\text{Undertone} = \text{Cool}$ if $a^* > b^*$ or $b^* < 10$
- $\text{Undertone} = \text{Neutral}$ otherwise

##### D. Color Harmony Harmonization
Maps classified tone to curated 4-season palettes (Spring: Warm & Light, Autumn: Warm & Deep, Summer: Cool & Light, Winter: Cool & Vivid) complete with hex codes, garment complementary contrasts, and styling rules.

---

### PHASE 7: Decoupled RAG Knowledge Engine & Vector Architecture (Model 4)

#### 1. Scope & Objective
Implement a production-grade Retrieval-Augmented Generation subsystem (`services/rag_service.py`, `services/gemini_llm.py`, `services/vector_db.py`) to answer styling, apparel care, sizing, and store policy inquiries with zero hallucination.

#### 2. Architectural Design Patterns (Ports & Adapters)
- **Port Interfaces:**
  - `core/interfaces/llm_provider.py`: `AbstractLLMProvider` with asynchronous method `generate_response(prompt: str, system_instruction: str) -> str`.
  - `core/interfaces/vector_store.py`: `AbstractVectorStore` with asynchronous methods `upsert(documents, metadatas, ids)` and `query(query_text, top_k) -> List[DocumentChunk]`.
- **Adapters:**
  - `GeminiLLMProvider`: Interfaces with Google Gemini API via official SDK / `httpx`.
  - `MockLLMProvider`: Deterministic fallback for local execution and unit tests when an API key is not provisioned.
  - `ChromaVectorStore`: Persistent vector store using local embeddings.
  - `InMemoryVectorStore`: Zero-dependency TF-IDF / Cosine similarity fallback ensuring the test harness and offline development environments never crash.

#### 3. Retrieval & Ingestion Pipeline
1. Load knowledge markdown files from `data/docs/`.
2. Segment texts with a recursive character splitter ($L=300$ tokens, overlap $O=50$ tokens).
3. Generate embeddings and store vectors with metadata tags (`topic`, `source`).
4. Query pipeline retrieves top-$k$ contextual chunks ($k=3$) and injects them into a constrained prompt envelope preventing out-of-domain hallucinations.

---

### PHASE 8: Production FastAPI Microservice & Clean Architecture Scaffolding

#### 1. Scope & Objective
Assemble the presentation layer in `app/` exposing high-performance, asynchronous REST endpoints backed by Pydantic v2 schemas and strict validation.

#### 2. Endpoint Specifications & Contracts

##### A. `POST /api/v1/fit-check`
- **Request Body (Multipart Form or JSON):**
  - Option A: Raw images `front_image`, `side_image` + `height_cm`, `weight_kg`, `gender`.
  - Option B: Pre-extracted masks / base64 masks.
- **Response:**
  ```json
  {
    "status": "success",
    "measurements": {
      "chest_cm": 98.4,
      "waist_cm": 82.1,
      "hip_cm": 99.7
    },
    "calibration": {
      "scale_front": 0.182,
      "scale_side": 0.183,
      "bmi": 23.4
    },
    "latency_ms": 24.1
  }
  ```

##### B. `POST /api/v1/recommend`
- **Request Body:**
  ```json
  {
    "body_measurements": {"chest_cm": 98.4, "waist_cm": 82.1, "hip_cm": 99.7},
    "garment_spec": {"size": "M", "chest_cm": 102.0, "waist_cm": 86.0, "hip_cm": 104.0},
    "fabric_stretch": 0.05
  }
  ```
- **Response:**
  ```json
  {
    "fit_category": "Fit",
    "ease_chest_cm": 3.6,
    "verdict": "Size M provides an optimal fit with comfortable chest ease."
  }
  ```

##### C. `POST /api/v1/color-palette`
- **Request Body:** Facial crop image or base64 RGB patch.
- **Response:** Individual Typology Angle, undertone, classification, recommended hex palette.

##### D. `POST /api/v1/chat`
- **Request Body:** `{"query": "What is your return policy on intimate apparel?", "session_id": "uuid"}`.
- **Response:** Grounded contextual answer with retrieved document citations.

##### E. System Observability: `GET /health` and `GET /metrics`.

---

### PHASE 9: Comprehensive Automated Test Harness, Integration Verification & Benchmarking

#### 1. Scope & Objective
Implement a multi-tiered test suite in `tests/` utilizing `pytest` to guarantee deterministic correctness, performance regression protection, and error boundary safety.

#### 2. Test Coverage Matrix
1. `test_geometry.py`: Validates that Ramanujan elliptic approximation matches theoretical values within $0.01\%$. Validates bounding box scale invariance.
2. `test_regressor.py`: Validates model inference execution on real BodyM dataset samples, asserting output dimensions and physical realism ($50 \le \text{chest} \le 180\text{ cm}$).
3. `test_fit.py`: Tests boundary conditions around ease thresholds ($\Delta = -0.1 \to \text{Small}$, $\Delta = 3.0 \to \text{Fit}$, $\Delta = 8.0 \to \text{Large}$).
4. `test_color.py`: Tests synthetic skin swatches of known RGB values to verify accurate CIELAB and undertone classification.
5. `test_rag.py`: Tests vector document retrieval recall and prompt injection safety.
6. `test_api.py`: Validates HTTP status codes, Pydantic schema validation failures ($422$), and standard responses ($200$).

---

### PHASE 10: Operational Hardening, Model Card Documentation & Production Readiness

#### 1. Scope & Objective
Finalize system operational hygiene, edge case mitigations, performance profiling, and formal documentation.

#### 2. Edge Case Defenses & Fallbacks
- **Non-Standard Posture / Partial Silhouettes:** If the detected mask height is $<60\%$ of image height, return a descriptive `UNRELIABLE_SILHOUETTE_EXCEPTION` rather than silent numerical corruption.
- **High BMI / Morphological Outliers:** Soft bounding caps applied to prevent unbounded polynomial divergence.
- **Zero API Key Fallback:** The application boots cleanly and operates with local embeddings and deterministic rule-based advisory if third-party credentials are not supplied.
- **Model Card Formulation:** Formal documentation detailing training data provenance (BodyM dataset), demographic representation, intended use, limitations, and ethical considerations.

---

## 4. Architectural Summary & Immediate Execution Step

With this 10-phase master blueprint established, we now initiate Phase 1 and Phase 2: assembling the project scaffolding, verifying dependencies, constructing the geometric feature extraction engine, training the anthropometric regressor on the BodyM dataset, and building out the FastAPI microservice layer.
