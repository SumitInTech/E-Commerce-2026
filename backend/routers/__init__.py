"""Routers Package."""
from backend.routers.gateway_router import router as gateway_router
from backend.routers.auth_router import router as auth_router
from backend.routers.catalog_router import router as catalog_router
from backend.routers.order_router import router as order_router
from backend.routers.payment_router import router as payment_router
from backend.routers.admin_router import router as admin_router
from backend.routers.ai_fit_router import router as ai_fit_router
from backend.routers.ai_chatbot_router import router as ai_chatbot_router

__all__ = [
    "gateway_router",
    "auth_router",
    "catalog_router",
    "order_router",
    "payment_router",
    "admin_router",
    "ai_fit_router",
    "ai_chatbot_router"
]
