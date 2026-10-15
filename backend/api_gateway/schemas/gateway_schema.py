"""
Pydantic v2 Schemas for API Gateway Health, Security & Routing.
"""
from typing import Dict, Any, List
from pydantic import BaseModel


class ServiceStatusDTO(BaseModel):
    name: str
    status: str
    port: int
    endpoint: str


class GatewayHealthResponse(BaseModel):
    status: str
    gateway_version: str
    active_connections: int
    services: Dict[str, Any]


class GatewayStatusResponse(BaseModel):
    gateway: str
    rate_limiter_active: bool
    sanitizer_active: bool
    registered_microservices: List[str]
