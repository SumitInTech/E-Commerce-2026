"""
Pydantic schemas for Anthropometric Measurement (Model 1).
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MeasurementRequest(BaseModel):
    height_cm: float = Field(..., ge=100.0, le=250.0, description="Subject height in centimeters")
    weight_kg: float = Field(..., ge=30.0, le=250.0, description="Subject weight in kilograms")
    gender: str = Field(..., description="Subject gender ('male' or 'female')")
    photo_id: Optional[str] = Field(None, description="Optional BodyM photo_id for testbench evaluation")
    front_mask_base64: Optional[str] = Field(None, description="Optional base64-encoded PNG silhouette (front)")
    side_mask_base64: Optional[str] = Field(None, description="Optional base64-encoded PNG silhouette (side)")


class MeasurementResponse(BaseModel):
    status: str = "success"
    predictions: Dict[str, float]
    extracted_features: Dict[str, float]
    model_type: str
    latency_ms: float
