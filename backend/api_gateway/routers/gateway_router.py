"""
API Gateway HTTP Router.
Registers gateway-level status, metrics, and health check endpoints.
"""
from fastapi import APIRouter
from backend.api_gateway.schemas.gateway_schema import GatewayHealthResponse, GatewayStatusResponse
from backend.api_gateway.controllers.gateway_controller import gateway_controller

router = APIRouter(prefix="/gateway", tags=["API Gateway Service"])


@router.get("/health", response_model=GatewayHealthResponse)
def gateway_health():
    """Aggregated health status across all 7 downstream platform microservices."""
    return gateway_controller.get_health()


@router.get("/status", response_model=GatewayStatusResponse)
def gateway_status():
    """Returns active traffic controls, rate limiting rules, and registered microservices."""
    return gateway_controller.get_status()
