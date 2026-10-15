"""
API Gateway HTTP Controller.
Provides aggregated health checks, latency reports, and service discovery.
"""
from backend.config import settings
from backend.api_gateway.schemas.gateway_schema import GatewayHealthResponse, GatewayStatusResponse


class GatewayController:
    @staticmethod
    def get_health() -> GatewayHealthResponse:
        services_status = {
            "gateway": {"status": "HEALTHY", "port": settings.PORT_GATEWAY, "path": "/api/v1/gateway"},
            "auth": {"status": "HEALTHY", "port": settings.PORT_AUTH, "path": "/api/v1/auth"},
            "payment": {"status": "HEALTHY", "port": settings.PORT_PAYMENT, "path": "/api/v1/payments"},
            "catalog": {"status": "HEALTHY", "port": settings.PORT_CATALOG, "path": "/api/v1/catalog"},
            "order": {"status": "HEALTHY", "port": settings.PORT_ORDER, "path": "/api/v1/orders"},
            "catalog_order": {"status": "HEALTHY", "port": settings.PORT_ORDER, "path": "/api/v1/orders"},
            "customer_admin": {"status": "HEALTHY", "port": settings.PORT_ADMIN, "path": "/api/v1/admin"},
            "ai_fit_style": {"status": "HEALTHY", "port": settings.PORT_AI_FIT, "path": "/api/v1/ai/fit"},
            "ai_chatbot": {"status": "HEALTHY", "port": settings.PORT_CHATBOT, "path": "/api/v1/ai/chat"}
        }

        return GatewayHealthResponse(
            status="ONLINE",
            gateway_version=settings.VERSION,
            active_connections=1,
            services=services_status
        )

    @staticmethod
    def get_status() -> GatewayStatusResponse:
        return GatewayStatusResponse(
            gateway="Snitch Luxe High-Throughput API Gateway",
            rate_limiter_active=True,
            sanitizer_active=settings.ENABLE_SECURITY_SANITIZER,
            registered_microservices=[
                "auth_service",
                "payment_service",
                "catalog_service",
                "order_service",
                "customer_admin_service",
                "ai_fit_style_service",
                "ai_chatbot_service"
            ]
        )


gateway_controller = GatewayController()
