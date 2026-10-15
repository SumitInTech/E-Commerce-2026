"""
Autonomous Catalog Microservice Application.
Can be executed as an independent container/process on port 8003.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.catalog.routers.catalog_router import router as catalog_router
from backend.database.supabase_client import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Catalog Microservice",
    version=settings.VERSION,
    description="Dedicated microservice managing streetwear catalogs, product specifications, and multi-point sizing charts."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"service": "catalog_service", "status": "HEALTHY", "port": settings.PORT_CATALOG}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.catalog.main:app", host="0.0.0.0", port=settings.PORT_CATALOG, reload=True)
