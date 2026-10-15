"""
Autonomous Order & Cart Microservice Application.
Can be executed as an independent container/process on port 8004.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.order.routers.order_router import router as order_router
from backend.database.supabase_client import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Order & Cart Microservice",
    version=settings.VERSION,
    description="Dedicated microservice orchestrating shopping carts, atomic checkouts, and 7-stage order tracking."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(order_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"service": "order_service", "status": "HEALTHY", "port": settings.PORT_ORDER}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.order.main:app", host="0.0.0.0", port=settings.PORT_ORDER, reload=True)
