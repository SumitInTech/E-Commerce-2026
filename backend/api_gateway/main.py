"""
API Gateway & Central Traffic Orchestrator.
Main reverse proxy application aggregating all 7 microservices behind a unified port.
"""
import time
import uuid
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import settings
from backend.database.supabase_client import init_db
from backend.api_gateway.services.gateway_service import rate_limiter, security_sanitizer

# Microservice Routers
from backend.api_gateway.routers.gateway_router import router as gateway_router
from backend.auth.routers.auth_router import router as auth_router
from backend.catalog.routers.catalog_router import router as catalog_router
from backend.order.routers.order_router import router as order_router
from backend.payment.routers.payment_router import router as payment_router
from backend.customer_admin.routers.admin_router import router as admin_router
from backend.ai_fit.routers.ai_fit_router import router as ai_fit_router
from backend.chatbot.routers.chatbot_router import router as chatbot_router

# Backward compatibility alias routers from autonomous microservices
from backend.ai_fit.routers.ai_fit_router import legacy_router as legacy_ai_fit_router
from backend.chatbot.routers.chatbot_router import legacy_router as legacy_chatbot_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan event handler replacing deprecated @app.on_event."""
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## Snitch Luxe AI E-Commerce Microservices Gateway
    
    Central reverse proxy orchestrating the 7 platform microservices:
    1. **API Gateway**: Traffic throttling, request tracing, attack sanitization.
    2. **Auth Service**: Buyer, Seller, and Admin JWT workflows with RBAC.
    3. **Payment Service**: Idempotent financial processing, gateway simulation, audit trails.
    4. **Catalog Service**: Streetwear product listings with multi-point anatomical size charts.
    5. **Order & Cart Service**: Atomic checkouts, cart management, and 7-stage order tracking.
    6. **Customer & Admin Service**: SLA ticketing, vendor onboarding, and executive analytics.
    7. **AI Fit & Style Service**: Anthropometric 3D regression & kinematic ease recommendations.
    8. **AI Chatbot Service**: Grounded RAG store policy & live database order fulfillment tracking.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gateway Middleware: Tracing, Rate Limiting & Threat Sanitization
@app.middleware("http")
async def gateway_orchestrator_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # 1. Rate Limiting Check (Bypass docs & openapi)
    path = request.url.path
    if path not in ["/docs", "/redoc", "/openapi.json", "/"]:
        client_ip = request.client.host if request.client else "127.0.0.1"
        is_allowed, remaining = rate_limiter.is_allowed(client_ip)
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Max {settings.RATE_LIMIT_REQUESTS_PER_MINUTE} requests/minute allowed per IP.",
                    "request_id": request_id
                },
                headers={"Retry-After": "60", "X-Request-ID": request_id}
            )

    # 2. Threat Sanitizer (Inspect Query Parameters)
    if settings.ENABLE_SECURITY_SANITIZER and request.query_params:
        raw_query = str(request.query_params)
        is_safe, threat_msg = security_sanitizer.inspect(raw_query)
        if not is_safe:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Security validation blocked malicious traffic",
                    "detail": threat_msg,
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )

    # 3. Dispatch to targeted microservice router
    response: Response = await call_next(request)

    # 4. Attach Distributed Tracing & Latency Auditing Headers
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Gateway"] = "Snitch-Luxe-v2.5"

    return response


# Mount all Microservices under API_V1_STR
app.include_router(gateway_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(catalog_router, prefix=settings.API_V1_STR)
app.include_router(order_router, prefix=settings.API_V1_STR)
app.include_router(payment_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(ai_fit_router, prefix=settings.API_V1_STR)
app.include_router(chatbot_router, prefix=settings.API_V1_STR)

# Backward-compatibility routes
app.include_router(legacy_ai_fit_router, prefix=settings.API_V1_STR)
app.include_router(legacy_chatbot_router, prefix=settings.API_V1_STR)


@app.get("/")
def root_discovery():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "gateway_docs": "/docs",
        "api_v1_root": settings.API_V1_STR,
        "health_check": f"{settings.API_V1_STR}/gateway/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api_gateway.main:app", host="0.0.0.0", port=settings.PORT_GATEWAY, reload=True)
