"""
Pydantic v2 Schemas for AI Body Measurements, Garment Fit & Color Palettes.
Includes compatibility aliases for both new microservice routes and legacy clients.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BodyScanRequest(BaseModel):
    height_cm: float = Field(..., ge=120, le=240, description="Height in cm")
    weight_kg: float = Field(..., ge=30, le=250, description="Weight in kg")
    gender: str = Field(default="male", description="'male' or 'female'")
    user_id: Optional[int] = None
    front_mask_base64: Optional[str] = None
    side_mask_base64: Optional[str] = None
    front_photo_base64: Optional[str] = None
    side_photo_base64: Optional[str] = None

    def model_post_init(self, __context):
        if not self.front_mask_base64 and self.front_photo_base64:
            self.front_mask_base64 = self.front_photo_base64
        if not self.side_mask_base64 and self.side_photo_base64:
            self.side_mask_base64 = self.side_photo_base64


# Backward-compatibility alias
BodyMeasurementPredictRequest = BodyScanRequest


class BodyMeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    height_cm: float
    weight_kg: float
    gender: str
    chest_cm: float
    waist_cm: float
    hip_cm: float
    bmi: float
    confidence_score: float = 0.94
    recommended_standard_size: str = "M"
    recommended_shirt_size: str = "M"
    recommended_pant_size: str = "32"
    recommended_pant_waist_inches: int = 32
    body_morphology: str = "Athletic V-Taper"
    status: str = "success"
    inference_mode: str = "biometric_prior"
    predictions: Optional[Dict[str, float]] = None
    extracted_features: Optional[Dict[str, Any]] = None

    def model_post_init(self, __context):
        if self.predictions is None:
            self.predictions = {
                "chest_cm": self.chest_cm,
                "waist_cm": self.waist_cm,
                "hip_cm": self.hip_cm
            }
        if not self.recommended_shirt_size:
            self.recommended_shirt_size = self.recommended_standard_size


class FitAdviceRequest(BaseModel):
    product_id: Optional[int] = None
    chest_cm: float = Field(..., gt=50, lt=200)
    waist_cm: float = Field(..., gt=40, lt=200)
    hip_cm: float = Field(..., gt=50, lt=200)
    garment_type: str = Field(default="shirt", description="'shirt', 'jacket', or 'pants'")
    target_size: Optional[str] = None
    garment_specs: Optional[Dict[str, float]] = None
    fabric_stretch: Optional[Any] = None


# Backward-compatibility alias
GarmentFitCheckRequest = FitAdviceRequest


class FitAdviceResponse(BaseModel):
    status: str = "success"
    recommended_size: str
    fit_category: str
    ease_allowance_cm: Dict[str, float]
    primary_ease_cm: Optional[float] = None
    weighted_average_ease_cm: Optional[float] = None
    return_risk_score: float = 0.05
    advice_note: str = ""
    size_advice: Optional[str] = None
    verdict: Optional[str] = None
    primary_dimension: str = "chest"
    dimension_breakdown: Optional[Dict[str, Any]] = None

    def model_post_init(self, __context):
        if self.primary_ease_cm is None:
            self.primary_ease_cm = self.ease_allowance_cm.get("chest_ease_cm", 6.0)
        if self.size_advice is None:
            self.size_advice = self.advice_note
        if self.verdict is None:
            self.verdict = self.advice_note


# Backward-compatibility alias
GarmentFitResponse = FitAdviceResponse


class ColorPaletteRequest(BaseModel):
    hex_color: Optional[str] = Field(None, description="Hex color of skin tone (e.g. #D4AA78)")
    r: Optional[int] = Field(None, ge=0, le=255)
    g: Optional[int] = Field(None, ge=0, le=255)
    b: Optional[int] = Field(None, ge=0, le=255)
    ita: Optional[float] = None
    image_base64: Optional[str] = Field(None, description="Uploaded portrait, selfie, or skin crop image in base64")


# Backward-compatibility alias
SkinTonePaletteRequest = ColorPaletteRequest


class ColorPaletteResponse(BaseModel):
    status: str = "success"
    input_hex: str
    detected_from_image: bool = False
    detected_skin_hex: Optional[str] = None
    skin_tone_category: str
    ita_angle: float
    ita_category: Optional[str] = None
    recommended_palette: str
    seasonal_tone: Optional[str] = None
    complementary_colors: List[str]
    best_colors: Optional[List[str]] = None
    color_names: Optional[List[str]] = None
    avoid_colors: List[str] = []
    styling_advice: str = ""
    styling_tips: Optional[str] = None
    palette_description: Optional[str] = None
    recommended_catalog_items: Optional[List[Dict[str, Any]]] = None

    def model_post_init(self, __context):
        if self.seasonal_tone is None:
            self.seasonal_tone = self.recommended_palette
        if self.best_colors is None:
            self.best_colors = self.complementary_colors
        if self.ita_category is None:
            self.ita_category = self.skin_tone_category
        if self.styling_tips is None:
            self.styling_tips = self.styling_advice
        if self.detected_skin_hex is None:
            self.detected_skin_hex = self.input_hex


# Backward-compatibility alias
SkinTonePaletteResponse = ColorPaletteResponse


class FullStylingRequest(BaseModel):
    height_cm: float = Field(..., ge=120, le=240)
    weight_kg: float = Field(..., ge=30, le=250)
    gender: str = Field(default="male")
    hex_skin_color: str = Field(default="#D2A080")
    product_id: Optional[int] = None
    garment_type: str = Field(default="shirt")


class FullStylingResponse(BaseModel):
    status: str = "success"
    user_profile: Dict[str, Any]
    predicted_measurements: Dict[str, float]
    recommended_size: str
    fit_analysis: Dict[str, Any]
    color_analysis: Dict[str, Any]
    personalized_styling_notes: str
