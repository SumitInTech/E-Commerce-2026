"""
Router for Model 3: Photometric CIELAB Skin-Tone & Seasonal Color Matcher.
"""
import base64
import numpy as np
import cv2
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.color import ColorAnalysisRequest, ColorAnalysisResponse
from app.dependencies import get_color_engine
from models.color.color_engine import ColorEngine

router = APIRouter(prefix="/api/v1", tags=["Model 3: Color Matching"])


def hex_to_rgb(hex_code: str) -> np.ndarray:
    """Converts hex color code to RGB pixel array."""
    hex_code = hex_code.lstrip("#")
    if len(hex_code) != 6:
        raise ValueError("Invalid hex color code format.")
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    # Return a 20x20 patch to allow clustering
    return np.full((20, 20, 3), [r, g, b], dtype=np.uint8)


@router.post("/color-palette", response_model=ColorAnalysisResponse)
def analyze_color(
    request: ColorAnalysisRequest,
    color_engine: ColorEngine = Depends(get_color_engine)
):
    """
    Analyzes skin tone via CIE L*a*b* color space, computes Individual Typology Angle (ITA),
    and generates a personalized seasonal color palette.
    """
    rgb_patch = None

    if request.image_base64:
        try:
            b64_str = request.image_base64
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            img_bytes = base64.b64decode(b64_str)
            nparr = np.frombuffer(img_bytes, np.uint8)
            bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if bgr is None:
                raise ValueError("Could not decode image")
            rgb_patch = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Failed to decode base64 image: {str(e)}")

    elif request.rgb_triplet:
        if len(request.rgb_triplet) != 3:
            raise HTTPException(status_code=422, detail="rgb_triplet must contain exactly 3 integers [R, G, B]")
        r, g, b = request.rgb_triplet
        rgb_patch = np.full((20, 20, 3), [r, g, b], dtype=np.uint8)

    elif request.rgb_hex:
        try:
            rgb_patch = hex_to_rgb(request.rgb_hex)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    else:
        # Default representative skin tone demo
        rgb_patch = np.full((20, 20, 3), [220, 175, 140], dtype=np.uint8)

    try:
        res = color_engine.analyze_skin_patch(rgb_patch)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Color analysis failed: {str(e)}")

    return ColorAnalysisResponse(
        status="success",
        cielab=res["cielab"],
        ita_degrees=res["ita_degrees"],
        ita_category=res["ita_category"],
        undertone=res["undertone"],
        season=res["season"],
        palette=res["palette"]
    )
