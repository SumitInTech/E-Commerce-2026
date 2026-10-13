# System Implementation & Architecture Plan

## 1. Project Overview & Architecture Design
The project is a unified Python 3.11 backend built on **FastAPI**. It handles four distinct AI/ML models specifically tailored for an e-commerce platform. The system is designed to be CPU-friendly and highly modular, ensuring components like the Vector Database and LLM providers can be swapped seamlessly in the future.

### Directory Structure Strategy
```text
project_root/
├── app/                  # FastAPI Application
│   ├── main.py           # Entry point
│   ├── routers/          # /fit-check, /chatbot, /recommend
│   └── schemas/          # Pydantic models for request/response validation
├── core/                 # Interfaces and Configs
│   ├── config.py         # .env parsing (Pydantic BaseSettings)
│   ├── interfaces/       # Abstract Base Classes (LLMProvider, VectorStore)
│   └── exceptions.py     # Custom error handling
├── models/               # Model weights and logic
│   ├── measurement/      # Model 1 logic & .pkl files
│   ├── color/            # Model 3 K-Means logic
│   └── fit/              # Model 2 Rule-based logic
├── data/                 # Training data and scripts
│   ├── train_pipeline.py # Script for training Model 1
│   ├── raw/              # Link to Test A/B, Train folders
│   └── docs/             # FAQs for RAG ingestion
└── services/             # Integrations (ChromaDB, Gemini API)
```

---

## 2. Model 1: Body Measurement Regressor (Training Pipeline)
**Goal:** Map 2D user photos (front & side) to real-world 3D measurements (chest, waist, hip).

### A. Data Processing & Feature Engineering
1. **Data Loading:** Read `subject_to_photo_map.csv` to map a user's ID to their corresponding front and side masks in the `train/train/mask` directories. Merge with `measurements.csv` (ground truth) and `hwg_metadata.csv` (height, weight).
2. **Geometric Feature Extraction (OpenCV):** 
   - Instead of standard keypoints (which fail on silhouettes), we will find the mask contours.
   - Using anatomical heuristics (e.g., shoulders at ~80% height, chest at ~75%, waist at ~60%, hips at ~50%), extract the **width** (from front mask) and **depth** (from side mask) in pixels.
3. **Pixel-to-CM Calibration:** 
   - We know the user's real `height_cm` and their `pixel_height` from the mask bounding box.
   - `cm_per_pixel = height_cm / pixel_height`
   - Calibrated Features: Multiply extracted pixel widths/depths by `cm_per_pixel`.
4. **Final Feature Vector (X):** `[calibrated_chest_width, calibrated_waist_width, calibrated_hip_depth, calibrated_hip_width, height_cm, weight_kg]`

### B. Training Technique
- **Algorithm:** `Ridge Regression` or `RandomForestRegressor` (CPU optimized, highly robust to collinear features).
- **Training Strategy:** Fit the regressor on the `train` split. 
- **Validation:** Evaluate on `BodyM Test-B` dataset. We will calculate the Mean Absolute Error (MAE). Target MAE is ~2-3 cm for chest/waist/hips.

### C. Inference Strategy (Production)
Since production inputs are raw user photos (not masks), we must ensure feature parity between training and serving.
- Use a pretrained lightweight segmentation model (e.g., `rembg` or `MediaPipe Selfie Segmentation`) to generate the mask from the raw photo on the fly.
- Pass the generated mask into the exact same Geometric Feature Extraction pipeline.

---

## 3. Model 2: Size Fit Recommender
**Goal:** Recommend sizing (Small / Fit / Large).

### Implementation Technique
- **Current Phase (Rule-Based):** Since the BodyM dataset lacks explicit fit labels (small/fit/large) and return reasons, we will rely on rule-based heuristics.
- **Metric:** `ease = garment_chest_cm - predicted_body_chest_cm`
- **Threshold Logic:**
  - `ease < 0 cm` ➡️ **Small** (Too tight)
  - `0 <= ease <= 6 cm` ➡️ **Fit** (Perfect fit)
  - `ease > 6 cm` ➡️ **Large** (Too loose)
- **Future-Proofing:** The function `get_fit_recommendation(body_profile, garment_specs)` will be structured so that once real platform data (orders + returns) is collected, the internal logic can be swapped out for a trained `LightGBM` classifier without changing the API contract.

---

## 4. Model 3: Skin Tone / Color Matcher
**Goal:** Recommend a color palette based on facial skin tone.

### Implementation Technique
1. **Face Detection:** Use OpenCV (`Haar Cascades` or `MediaPipe Face Mesh`) to isolate the face bounding box.
2. **Sampling & Filtering:** Extract a patch of skin from the cheeks/forehead, ignoring eyes/mouth.
3. **Clustering:** 
   - Convert RGB pixels to the **CIELAB (`Lab`) color space**, which separates luminance (lighting) from color channels (a, b), making it highly robust to shadows and indoor lighting.
   - Run **K-Means Clustering (k=3)** on the Lab pixels. Extract the dominant cluster centroid.
4. **Rule Table Integration:** Map the dominant Lab centroid to a tone category (Warm, Cool, Neutral) using predefined heuristic thresholds. Return a hardcoded stylist color palette.

---

## 5. Model 4: RAG Chatbot (Support & Recommendation)
**Goal:** Answer customer queries based on the store's knowledge base.

### Architecture & Tools
- **LLM Provider:** Gemini API (Accessed securely via `.env` file).
- **Vector Database:** ChromaDB (Running locally, persistent storage).

### Implementation Technique
1. **Interface Design:** 
   - Create an `LLMProvider` Interface. (Allows swapping Gemini for OpenAI later).
   - Create a `VectorStore` Interface. (Allows migrating from ChromaDB to PostgreSQL `pgvector` seamlessly).
2. **Ingestion Pipeline (Offline):**
   - Read dummy FAQ/Policy `.md` files.
   - Use a text splitter (e.g., overlapping chunks of 300 words).
   - Generate embeddings using Gemini's embedding model.
   - Upsert vectors + metadata into ChromaDB.
3. **Query Pipeline (Online /chatbot router):**
   - Receive user query.
   - Embed query ➡️ ChromaDB Similarity Search (top k=3).
   - Construct prompt: *"You are an AI stylist and support agent. Using ONLY the following context, answer the user's question..."*
   - Call Gemini API for the final generated response.

---

## 6. Execution Roadmap
*This is the order in which the code will be written once confirmed:*

1. **Step 1: Scaffolding & Configuration** - Setup FastAPI, `.env` parsing, and dependency injection.
2. **Step 2: Interfaces & RAG Chatbot** - Implement `LLMProvider`, `VectorStore`, ChromaDB, and the `/chatbot` endpoint. Test end-to-end.
3. **Step 3: Feature Extraction Pipeline** - Build the OpenCV mask contour extraction script and verify pixel-to-cm calibration logic.
4. **Step 4: Model 1 Training** - Execute the training script on the `train` dataset, validate on `testB`, and save the `.pkl` artifact.
5. **Step 5: Remaining Models & Integration** - Implement Model 2 (Fit Rules) and Model 3 (Color K-Means). Connect everything to the `/fit-check` and `/recommend` FastAPI endpoints.
