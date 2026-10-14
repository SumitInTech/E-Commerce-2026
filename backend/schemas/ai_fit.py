"""
AI Fit & Style Service Schemas.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class BodyMeasurementPredictRequest(BaseModel):
    height_cm: float = Field(..., ge=120.0, le=250.0, description="Height in centimeters")
    weight_kg: float = Field(..., ge=30.0, le=250.0, description="Weight in kilograms")
    gender: str = Field("male", description="'male' or 'female'")
    front_mask_base64: Optional[str] = None
    side_mask_base64: Optional[str] = None


class BodyMeasurementResponse(BaseModel):
    status: str = "success"
    inference_mode: str
    height_cm: float
    weight_kg: float
    gender: str
    predictions: Dict[str, float]  # chest_cm, waist_cm, hip_cm
    extracted_features: Optional[Dict[str, float]] = None


class GarmentFitCheckRequest(BaseModel):
    chest_cm: float = Field(..., ge=50.0, le=180.0)
    waist_cm: float = Field(..., ge=40.0, le=180.0)
    hip_cm: float = Field(..., ge=50.0, le=200.0)
    product_id: Optional[int] = None
    garment_type: str = "shirt"
    fabric_stretch: str = "none"
    garment_specs: Optional[Dict[str, float]] = None


class GarmentFitResponse(BaseModel):
    status: str = "success"
    recommended_size: str
    evaluated_garment_size: Optional[str] = None
    fit_category: str  # Small, Fit, Large
    size_advice: str
    primary_dimension: str
    primary_ease_cm: float
    weighted_average_ease_cm: float
    return_risk_score: float
    verdict: str
    dimension_breakdown: Dict[str, Any] = {}


class SkinTonePaletteRequest(BaseModel):
    hex_color: Optional[str] = "#E0AC69"
    ita: Optional[float] = None
    image_base64: Optional[str] = None


class SkinTonePaletteResponse(BaseModel):
    status: str = "success"
    ita_angle: float
    ita_category: str
    seasonal_tone: str
    palette_description: str
    best_colors: List[str]
    color_names: List[str]
    avoid_colors: List[str]
    styling_tips: str
    recommended_catalog_items: List[Dict[str, Any]] = []


class FullStylingRequest(BaseModel):
    height_cm: float = 178.0
    weight_kg: float = 75.0
    gender: str = "male"
    hex_skin_color: str = "#E0AC69"
    product_id: Optional[int] = 1


class FullStylingResponse(BaseModel):
    status: str = "success"
    user_profile: Dict[str, Any]
    predicted_measurements: Dict[str, float]
    recommended_size: str
    fit_analysis: Dict[str, Any]
    color_analysis: Dict[str, Any]
    personalized_styling_notes: str
