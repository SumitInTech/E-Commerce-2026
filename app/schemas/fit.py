"""
Pydantic schemas for Garment Fit Recommendation (Model 2).
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class FitEvaluationRequest(BaseModel):
    body_measurements: Dict[str, float] = Field(
        ...,
        json_schema_extra={"example": {"chest": 98.4, "waist": 82.1, "hip": 99.7}},
        description="Body measurements in centimeters"
    )
    garment_specs: Optional[Dict[str, float]] = Field(
        None,
        json_schema_extra={"example": {"chest": 102.0, "waist": 86.0, "hip": 104.0}},
        description="Garment specifications for a specific size in cm"
    )
    fabric_stretch: float = Field(0.0, ge=0.0, le=0.5, description="Elastane/spandex stretch ratio")


class SizeRecommendationRequest(BaseModel):
    body_measurements: Dict[str, float] = Field(
        ...,
        json_schema_extra={"example": {"chest": 98.4, "waist": 82.1, "hip": 99.7}}
    )
    size_chart: Optional[Dict[str, Dict[str, float]]] = Field(
        None,
        description="Custom brand size chart mapping (e.g. {'S': {'chest': 92, ...}})"
    )
    fabric_stretch: float = Field(0.0, ge=0.0, le=0.5)


class FitResponse(BaseModel):
    status: str = "success"
    recommended_size: Optional[str] = None
    fit_category: str
    primary_ease_cm: float
    verdict: str
    ease_breakdown: Dict[str, Any]
