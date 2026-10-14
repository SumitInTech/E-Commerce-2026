"""Schemas package."""
from backend.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse
from backend.schemas.catalog import ProductResponse, CategoryResponse, ProductCreateRequest, ProductSizeResponse
from backend.schemas.order import CartItemAddRequest, CartResponse, CheckoutRequest, OrderResponse, OrderStatusUpdateRequest
from backend.schemas.payment import PaymentIntentRequest, PaymentProcessRequest, PaymentResponse, WebhookEventRequest
from backend.schemas.admin import TicketCreateRequest, TicketResponse, TicketUpdateRequest, VendorApplyRequest, PlatformMetricsResponse
from backend.schemas.ai_fit import (
    BodyMeasurementPredictRequest, BodyMeasurementResponse,
    GarmentFitCheckRequest, GarmentFitResponse,
    SkinTonePaletteRequest, SkinTonePaletteResponse,
    FullStylingRequest, FullStylingResponse
)
from backend.schemas.chatbot import ChatbotQueryRequest, ChatbotQueryResponse, CitationItem

__all__ = [
    "UserRegisterRequest", "UserLoginRequest", "TokenResponse", "UserProfileResponse",
    "ProductResponse", "CategoryResponse", "ProductCreateRequest", "ProductSizeResponse",
    "CartItemAddRequest", "CartResponse", "CheckoutRequest", "OrderResponse", "OrderStatusUpdateRequest",
    "PaymentIntentRequest", "PaymentProcessRequest", "PaymentResponse", "WebhookEventRequest",
    "TicketCreateRequest", "TicketResponse", "TicketUpdateRequest", "VendorApplyRequest", "PlatformMetricsResponse",
    "BodyMeasurementPredictRequest", "BodyMeasurementResponse", "GarmentFitCheckRequest", "GarmentFitResponse",
    "SkinTonePaletteRequest", "SkinTonePaletteResponse", "FullStylingRequest", "FullStylingResponse",
    "ChatbotQueryRequest", "ChatbotQueryResponse", "CitationItem"
]
