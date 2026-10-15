"""
Autonomous Customer Support & Admin Microservice Application.
Can be executed as an independent container/process on port 8005.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.customer_admin.routers.admin_router import router as admin_router
from backend.database.supabase_client import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Customer & Admin Microservice",
    version=settings.VERSION,
    description="Dedicated microservice handling support ticketing, vendor onboarding, and executive analytics."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"service": "customer_admin_service", "status": "HEALTHY", "port": settings.PORT_ADMIN}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.customer_admin.main:app", host="0.0.0.0", port=settings.PORT_ADMIN, reload=True)
