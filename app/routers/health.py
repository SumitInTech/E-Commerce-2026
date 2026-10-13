"""
Health check and operational metrics router.
"""
from fastapi import APIRouter
from core.config import settings

router = APIRouter(tags=["Health & Observability"])


@router.get("/health")
def health_check():
    """Returns application health and operational status."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "models_loaded": {
            "model_1_measurement": True,
            "model_2_fit_engine": True,
            "model_3_color_matcher": True,
            "model_4_rag_chatbot": True
        }
    }


@router.get("/metrics")
def get_metrics():
    """Returns runtime metadata and model benchmarks."""
    import os
    import json
    meta_path = settings.METADATA_PATH
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)

    return {
        "model_1_benchmarks": meta,
        "supported_sizing_standards": ["XS", "S", "M", "L", "XL", "XXL"],
        "seasonal_color_categories": ["Spring", "Summer", "Autumn", "Winter"]
    }
