"""
Autonomous Payment Microservice Application.
Can be executed as an independent container/process on port 8002.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.payment.routers.payment_router import router as payment_router
from backend.database.supabase_client import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Payment Microservice",
    version=settings.VERSION,
    description="Dedicated microservice handling financial transactions, gateway simulations, and idempotency guarantees."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"service": "payment_service", "status": "HEALTHY", "port": settings.PORT_PAYMENT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.payment.main:app", host="0.0.0.0", port=settings.PORT_PAYMENT, reload=True)
