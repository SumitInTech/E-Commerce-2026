"""
Pydantic schemas for Photometric Skin Tone & Color Palette Matching (Model 3).
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ColorAnalysisRequest(BaseModel):
    rgb_hex: Optional[str] = Field(None, json_schema_extra={"example": "#E0AC69"}, description="Hexadecimal skin swatch color")
    rgb_triplet: Optional[List[int]] = Field(None, json_schema_extra={"example": [224, 172, 105]}, description="RGB list [R, G, B]")
    image_base64: Optional[str] = Field(None, description="Base64 encoded skin patch or facial image crop")


class ColorAnalysisResponse(BaseModel):
    status: str = "success"
    cielab: Dict[str, float]
    ita_degrees: float
    ita_category: str
    undertone: str
    season: str
    palette: Dict[str, Any]
