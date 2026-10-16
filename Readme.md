# Snitch Luxe AI E-Commerce Platform

> **Production-Grade Microservices Architecture, Computer Vision Anthropometrics, and Luxury Streetwear E-Commerce Experience.**

---

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start Guide](#-quick-start-guide)
  - [1. Backend Setup & Run](#1-backend-setup--run)
  - [2. Running the Next.js Frontend](#2-running-the-nextjs-frontend)
  - [3. Running Autonomous Microservices Individually](#3-running-autonomous-microservices-individually)
- [Environment Configuration (`.env`)](#-environment-configuration-env)
- [Testing & Verification](#-testing--verification)
- [Pre-Seeded Test Credentials](#-pre-seeded-test-credentials)
- [October 15th Critical Stability Changelog](#-october-15th-critical-stability-changelog)
- [API Endpoints Reference](#-api-endpoints-reference)

---

## 🌟 Project Overview

This repository houses an enterprise e-commerce platform built to solve digital fashion retail's biggest bottleneck: **apparel returns caused by sizing uncertainty (25%–40% industry average)**.

The system combines:
1. **Autonomous Python Microservices (`backend/`):** Clean Architecture powered by FastAPI, SQLAlchemy, and connection-pooled databases.
2. **AI Model Hub (`ai_models/`):**
   - **Model 1 (Anthropometric Regressor):** Dual-view 2D contour slicing and Ramanujan ellipse circumference estimation.
   - **Model 2 (Garment Fit Engine):** Parametric ease kinematics predicting Small / Fit / Large.
   - **Model 3 (Photometric Color Matcher):** CIELAB Euclidean color space and Individual Typology Angle ($\text{ITA}^\circ$) styling.
   - **Model 4 (RAG Advisory Chatbot):** Semantic document search backed by Google Gemini and live database order fulfillment tracking.
3. **Luxury Streetwear Frontend (`frontend/`):** Next.js 15 (React 19) high-contrast urban storefront with interactive modals for AI biometrics, color profiling, cart drawer, and 5-stage order tracking.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│               Next.js 15 Frontend Storefront (Port 3000)                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST (CORS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│            API Gateway & Reverse Proxy (Port 8000: /api/v1)            │
│       [Sliding-Window Rate Limiter | Threat Sanitizer | Tracing]       │
└───────┬────────────┬─────────────┬─────────────┬───────────┬───────────┘
        │            │             │             │           │
        ▼            ▼             ▼             ▼           ▼
   Auth Service  Catalog      Order & Cart   Payment    Customer/Admin
    (Port 8001)  (Port 8003)   (Port 8004)  (Port 8002)   (Port 8005)
        │                                         │
        └─────────────────┬───────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │  AI Model Hub & RAG Services     │
        │  ai_fit: Port 8006               │
        │  chatbot: Port 8007              │
        └─────────────────┬────────────────┘
                          ▼
            [SQLite / Supabase PostgreSQL]
```

---

## ⚙️ Prerequisites

- **Python:** `3.11` to `3.13`
- **Node.js:** `v18.0.0` or higher (for frontend)
- **Git** (recommended)

---

## 🚀 Quick Start Guide

### 1. Backend Setup & Run

#### Step A: Open PowerShell or Terminal in the project root:
```powershell
cd c:\Users\ADMIN\Downloads\E-Commerce-2026-main
```

#### Step B: Create and activate a Python virtual environment (recommended):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Step C: Install dependencies:
```powershell
pip install -r backend/requirements.txt
```

#### Step D: Environment Configuration:
An active `.env` file is already generated in the root directory. To inspect or customize it:
```powershell
# Copy template if starting fresh:
copy .env.example .env
```

#### Step E: Start the Unified API Gateway:
```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive API Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Gateway Health Check:** [http://127.0.0.1:8000/api/v1/gateway/health](http://127.0.0.1:8000/api/v1/gateway/health)

---

### 2. Running the Next.js Frontend

Open a new terminal tab and run:

```powershell
cd c:\Users\ADMIN\Downloads\E-Commerce-2026-main\frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser. The frontend will communicate directly with the backend API Gateway at `http://127.0.0.1:8000/api/v1`.

---

### 3. Running Autonomous Microservices Individually

Every microservice can run independently in isolated containers or dedicated ports:

| Service | Port | Terminal Command |
| :--- | :--- | :--- |
| **API Gateway** | `8000` | `uvicorn backend.api_gateway.main:app --port 8000 --reload` |
| **Auth Service** | `8001` | `uvicorn backend.auth.main:app --port 8001 --reload` |
| **Payment Service** | `8002` | `uvicorn backend.payment.main:app --port 8002 --reload` |
| **Catalog Service** | `8003` | `uvicorn backend.catalog.main:app --port 8003 --reload` |
| **Order & Cart Service** | `8004` | `uvicorn backend.order.main:app --port 8004 --reload` |
| **Customer & Admin Service** | `8005` | `uvicorn backend.customer_admin.main:app --port 8005 --reload` |
| **AI Fit & Style Service** | `8006` | `uvicorn backend.ai_fit.main:app --port 8006 --reload` |
| **AI Chatbot Service** | `8007` | `uvicorn backend.chatbot.main:app --port 8007 --reload` |

---

## 🔐 Environment Configuration (`.env`)

The project uses Pydantic V2 `BaseSettings` which reads variables from `.env` in the project root or `backend/`. Key parameters include:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `snitch-super-secure...` | Cryptographic secret for signing HS256 JWT auth tokens. |
| `DATABASE_URL` | `sqlite:///./ecommerce.db` | Local SQLite database bundled with pre-seeded data. |
| `SUPABASE_DB_URL` | `""` | Optional PostgreSQL connection string. Supersedes SQLite if populated. |
| `PAYMENT_SIMULATION_MODE` | `True` | Simulates instant checkout payments without third-party fees. |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `120` | Gateway sliding-window request throttling per IP. |
| `GEMINI_API_KEY` | `""` | Optional Google AI Studio key. If left blank, offline RAG fallback is used. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name for conversational RAG queries. |

---

## 🧪 Testing & Verification

The codebase includes an automated test harness covering all microservices, API routes, and machine learning components:

```powershell
# Run the entire test suite:
python -m pytest backend/tests/ -v

# Run dedicated microservices architecture tests:
python -m pytest backend/tests/test_microservices_architecture.py -v
```

**Expected Result:** **`39 passed, 1 skipped`** (100% pass rate).

---

## 🔑 Pre-Seeded Test Credentials

The database comes pre-seeded with sample users for all three platform roles:

| Role | Email | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@snitch.com` | `Admin@12345` | View GMV analytics, manage support tickets, review seller applications |
| **Seller** | `seller@snitch.com` | `Seller@12345` | Catalog management, vendor inventory tracking |
| **Buyer** | `buyer@snitch.com` | `Buyer@12345` | Cart checkouts, AI body scans, order tracking |

---

## 🛠️ October 15th Critical Stability Changelog

During the stabilization sprint on **October 15th**, 8 major architectural issues were resolved across backend microservices:

1. **`backend/config.py` (Pydantic v2 Upgrade):**
   - *Problem:* Deprecated `class Config` threw runtime warnings on Python 3.13.
   - *Fix:* Modernized to `ConfigDict(extra="ignore", env_file=(".env", "../.env"))`.
2. **`backend/auth/` (Email Validation Zero-Dependency):**
   - *Problem:* Missing `email_validator` package caused container startup crashes.
   - *Fix:* Implemented RFC-compliant zero-dependency regex pattern validator in `UserRegisterRequest`.
3. **`backend/catalog/` (Database Schema Compatibility):**
   - *Problem:* `Product.title` vs `Product.name` mismatch caused SQLite operational errors.
   - *Fix:* Added property aliases and synonyms bridging legacy `name` and modern `title`.
4. **`backend/payment/` (Idempotency Unique Constraint):**
   - *Problem:* Replaying an idempotent payment raised `IntegrityError: UNIQUE constraint failed`.
   - *Fix:* Added cache existence guard in `PaymentController` to replay transactions without re-inserting records.
5. **`backend/ai_fit/` (Model Output Unpacking):**
   - *Problem:* Nested dictionary structure `{"predictions": {"chest_cm": ...}}` triggered HTTP 500.
   - *Fix:* Aligned DTO unmarshaling with `UnifiedAIHub.predict_measurements` contracts.
6. **`backend/ai_fit/` (Keyword Argument Signature Parity):**
   - *Problem:* Unsupported kwargs (`target_size`, `rgb`) threw `TypeError`.
   - *Fix:* Normalized signatures and converted RGB tuples to canonical hex color codes.
7. **`backend/order/` (SQLite Parameter Binding):**
   - *Problem:* Positional parameter swap caused SQLite binding error on `CartItemAddRequest`.
   - *Fix:* Enforced keyword arguments and defensive type checks in `order_service.add_to_cart`.
8. **Monolith Clean-Up & Legacy Purge:**
   - *Problem:* Redundant legacy folders (`backend/routers/`, `backend/services/`, etc.) caused circular imports.
   - *Fix:* Completely removed all dead monolithic code; integrated legacy router aliases into `ai_fit` and `chatbot`.
9. **Environment & Multi-Directory Parity (October 16th):**
   - *Problem:* Incomplete `.env.example` and missing parent-directory `.env` resolution.
   - *Fix:* Synchronized `.env.example`, created active `.env`, and enabled multi-path discovery in `Settings`.

---

## 📡 API Endpoints Reference

### API Gateway (`http://127.0.0.1:8000/api/v1`)
- `GET /gateway/health` - Downstream microservices health check
- `GET /gateway/status` - Traffic metrics and active route table

### Auth Service
- `POST /auth/register` - Create Buyer, Seller, or Admin account
- `POST /auth/login` - Authenticate and receive JWT token
- `GET /auth/me` - Fetch authenticated user profile

### Catalog Service
- `GET /catalog/categories` - List garment categories
- `GET /catalog/products` - List products with optional category filter
- `GET /catalog/sizes/{product_id}` - Fetch multi-point anatomical size charts

### Order & Cart Service
- `GET /orders/cart/{user_id}` - Retrieve active cart
- `POST /orders/cart/add` - Add garment item and size to cart
- `POST /orders/checkout` - Atomic order creation with stock reservation
- `GET /orders/track/{tracking_ref}` - 5-stage fulfillment timeline tracking

### Payment Service
- `POST /payments/process` - Idempotent payment processing (Card / UPI / COD)
- `GET /payments/transaction/{id}` - Transaction status lookup
- `POST /payments/refund` - Process refund for completed transactions

### AI Fit & Styling Service
- `POST /ai/fit/measure` - Predict chest, waist, and hip circumferences
- `POST /ai/fit/recommend` - Sizing ease recommendation (Small / Fit / Large)
- `POST /ai/fit/palette` - CIELAB skin-tone analysis and seasonal color harmonies

### AI Chatbot Service
- `POST /ai/chat/query` - RAG semantic policy Q&A and live order status lookup
- `GET /ai/chat/history/{session_id}` - Retrieve conversational history
