"""
API Gateway Router.
Provides platform health diagnostics and gateway telemetry.
"""
from fastapi import APIRouter
from backend.services.gateway_service import ServiceHealthRegistry

router = APIRouter(prefix="/gateway", tags=["1. API Gateway Service"])


@router.get("/health")
def health_check():
    """Returns real-time health and protocol status across all 7 platform services."""
    return {
        "status": "ONLINE",
        "platform": "Snitch Enterprise AI Microservices",
        "services": ServiceHealthRegistry.get_status()
    }


@router.get("/status")
def gateway_status():
    """Quick gateway liveness probe for Kubernetes / Docker container health checks."""
    return {"status": "ok", "healthy": True}
