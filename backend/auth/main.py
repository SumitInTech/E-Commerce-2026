"""
Autonomous Auth Microservice Application.
Can be executed as an independent container/process on port 8001.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.auth.routers.auth_router import router as auth_router
from backend.database.supabase_client import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Auth Microservice",
    version=settings.VERSION,
    description="Dedicated microservice handling user authentication, PBKDF2 cryptography, and RBAC JWT workflows."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"service": "auth_service", "status": "HEALTHY", "port": settings.PORT_AUTH}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.auth.main:app", host="0.0.0.0", port=settings.PORT_AUTH, reload=True)
