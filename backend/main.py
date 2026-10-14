"""
========================================================================================
ENTERPRISE API GATEWAY & MICROSERVICES ORCHESTRATOR
========================================================================================
Author: Senior Principal ML Systems Architect & Enterprise Designer
Module: backend.main
Description:
    Central API Gateway unifying all 7 core platform services:
    1. API Gateway Service (Access controls, rate limiting, attack sanitization, tracing)
    2. Auth Service (Buyer, Seller, Admin JWT RBAC workflows)
    3. Payment Service (Idempotent transactions, gateway simulations, audit trails)
    4. Order & Catalog Service (Product inventory, multi-point size charts, cart & orders)
    5. Customer & Admin Service (Ticketing triage, vendor onboarding, platform metrics)
    6. AI Fit & Style Service (Direct bridge to ai_models.main_model)
    7. AI Chatbot Service (RAG store policy & live database order tracking)

Usage:
    uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
========================================================================================
"""
import sys
import os
import time
import uuid
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path so backend and ai_models are discovered
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import settings
from backend.database import init_db
from backend.services.gateway_service import rate_limiter, SecuritySanitizer
from backend.routers import (
    gateway_router,
    auth_router,
    catalog_router,
    order_router,
    payment_router,
    admin_router,
    ai_fit_router,
    ai_chatbot_router
)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## Snitch Luxe AI E-Commerce Platform Services
    
    Unified enterprise architecture providing modern men's luxury fast-fashion
    powered by 4 specialized computer vision & natural language AI models.
    
    ### Integrated Services:
    1. **API Gateway**: Centralized rate limiting, request tracing, malicious traffic sanitization.
    2. **Auth Service**: Buyer, Seller, and Admin JWT workflows with role-based access control.
    3. **Payment Service**: Idempotent financial processing, gateway simulation (Card, UPI, COD), audit logging.
    4. **Order & Catalog Service**: Authoritative product catalog with multi-point size charts and cart management.
    5. **Customer & Admin Service**: Support ticketing, vendor onboarding, and executive business metrics.
    6. **AI Fit & Style Service**: Anthropometric 3D body circumference regression and kinematic ease recommendation.
    7. **AI Chatbot Service**: Real-time customer support grounded in store policy and live order fulfillment tracking.
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# -----------------------------------------------------------------------------
# CORS Middleware
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Gateway Middleware: Tracing, Latency Auditing, Rate Limiting & Security Sanitizer
# -----------------------------------------------------------------------------
@app.middleware("http")
async def gateway_orchestrator_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # 1. Rate Limiting Check (Bypass Swagger docs and gateway root discovery)
    path = request.url.path
    if path not in ["/docs", "/redoc", "/openapi.json", "/"]:
        client_ip = request.client.host if request.client else "127.0.0.1"
        is_allowed, remaining = rate_limiter.is_allowed(client_ip)
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please wait 60 seconds before retrying.",
                    "request_id": request_id
                },
                headers={"Retry-After": "60", "X-Request-ID": request_id}
            )

    # 2. Security Inspection for malicious patterns in query parameters
    query_str = str(request.url.query)
    is_safe, threat_desc = SecuritySanitizer.inspect(query_str)
    if not is_safe:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Malicious traffic detected",
                "detail": threat_desc,
                "request_id": request_id
            },
            headers={"X-Request-ID": request_id}
        )

    # 3. Process Request
    response: Response = await call_next(request)

    # 4. Attach Distributed Tracing & Latency Headers
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    response.headers["X-Service-Gateway"] = "FastAPI-Enterprise-v2"

    return response


# -----------------------------------------------------------------------------
# Mount Domain Service Routers under /api/v1
# -----------------------------------------------------------------------------
app.include_router(gateway_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(catalog_router, prefix=settings.API_V1_STR)
app.include_router(order_router, prefix=settings.API_V1_STR)
app.include_router(payment_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(ai_fit_router, prefix=settings.API_V1_STR)
app.include_router(ai_chatbot_router, prefix=settings.API_V1_STR)


# -----------------------------------------------------------------------------
# Microservices Root & Discovery Endpoint
# -----------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def gateway_root_info():
    """Enterprise API Gateway discovery endpoint."""
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "architecture": "Microservices Orchestration Gateway",
        "api_documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "frontend": "Next.js 15 Luxury App Router (http://localhost:3000)",
        "services": [
            {"name": "API Gateway", "prefix": f"{settings.API_V1_STR}/gateway"},
            {"name": "Auth Service", "prefix": f"{settings.API_V1_STR}/auth"},
            {"name": "Catalog Service", "prefix": f"{settings.API_V1_STR}/catalog"},
            {"name": "Order Service", "prefix": f"{settings.API_V1_STR}/orders"},
            {"name": "Payment Service", "prefix": f"{settings.API_V1_STR}/payments"},
            {"name": "Customer & Admin Service", "prefix": f"{settings.API_V1_STR}/admin"},
            {"name": "AI Fit & Style Service", "prefix": f"{settings.API_V1_STR}/ai/fit"},
            {"name": "AI Chatbot Service", "prefix": f"{settings.API_V1_STR}/ai/chat"},
        ]
    }


# -----------------------------------------------------------------------------
# Application Startup Event
# -----------------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    print("[Gateway Startup] Initializing Database & Seeding Snitch Catalog...")
    init_db()
    print("[Gateway Startup] Database schema synchronized and seed data validated.")
    print("[Gateway Startup] All 7 Platform Services mounted and healthy.")


if __name__ == "__main__":
    import uvicorn
    print("\nStarting Snitch Luxe Enterprise Gateway at http://127.0.0.1:8000 ...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
