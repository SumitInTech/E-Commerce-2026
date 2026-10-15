"""
Autonomous AI Fit & Style Microservice Application.
Can be executed as an independent container/process on port 8006.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.ai_fit.routers.ai_fit_router import router as fit_router
from backend.database.supabase_client import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - AI Fit & Style Microservice",
    version=settings.VERSION,
    description="Dedicated microservice executing CPU/GPU computer vision anthropometry, kinematic ease tolerance bands, and photometric color harmonies."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fit_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"service": "ai_fit_service", "status": "HEALTHY", "port": settings.PORT_AI_FIT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.ai_fit.main:app", host="0.0.0.0", port=settings.PORT_AI_FIT, reload=True)
