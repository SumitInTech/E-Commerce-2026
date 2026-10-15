"""
AI Fit & Style API Router.
Registers HTTP endpoints for body regression, garment ease recommendations, and color palettes.
Includes legacy_router alias mounted under /ai-fit for backward compatibility.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.supabase_client import get_db
from backend.ai_fit.schemas.fit_schema import (
    BodyScanRequest,
    BodyMeasurementResponse,
    FitAdviceRequest,
    FitAdviceResponse,
    ColorPaletteRequest,
    ColorPaletteResponse,
    FullStylingRequest,
    FullStylingResponse
)
from backend.ai_fit.controllers.fit_controller import ai_fit_controller

# Autonomous Microservice Router
router = APIRouter(prefix="/ai/fit", tags=["AI Fit & Style Service"])


@router.post("/measurements", response_model=BodyMeasurementResponse)
def estimate_measurements(req: BodyScanRequest, db: Session = Depends(get_db)):
    """Model 1: Anthropometric body circumference estimation (Chest, Waist, Hip)."""
    return ai_fit_controller.estimate_measurements(db, req)


@router.post("/recommend", response_model=FitAdviceResponse)
def get_fit_recommendation(req: FitAdviceRequest, db: Session = Depends(get_db)):
    """Model 2: Garment kinematic ease calculation & sizing recommendation."""
    return ai_fit_controller.get_fit_advice(req, db=db)


@router.post("/color-palette", response_model=ColorPaletteResponse)
def match_color_palette(req: ColorPaletteRequest, db: Session = Depends(get_db)):
    """Model 3: Photometric CIELAB skin-tone profiling & seasonal color matching."""
    return ai_fit_controller.get_color_palette(req, db=db)


@router.post("/vip-styling", response_model=FullStylingResponse)
async def vip_styling(req: FullStylingRequest, db: Session = Depends(get_db)):
    """VIP Multi-Model Pipeline: Models 1, 2, and 3 chained consultation."""
    return await ai_fit_controller.run_vip_styling(db, req)


# Legacy Compatibility Router (/api/v1/ai-fit/*)
legacy_router = APIRouter(prefix="/ai-fit", tags=["AI Fit & Style (Legacy Alias)"])


@legacy_router.post("/predict-measurements", response_model=BodyMeasurementResponse)
def legacy_predict_measurements(req: BodyScanRequest, db: Session = Depends(get_db)):
    """Model 1 Biometrics Regressor."""
    return ai_fit_controller.estimate_measurements(db, req)


@legacy_router.post("/evaluate-garment-fit", response_model=FitAdviceResponse)
def legacy_evaluate_garment_fit(req: FitAdviceRequest, db: Session = Depends(get_db)):
    """Model 2 Kinematic Ease & Sizing Engine."""
    return ai_fit_controller.get_fit_advice(req, db=db)


@legacy_router.post("/color-palette", response_model=ColorPaletteResponse)
def legacy_color_palette(req: ColorPaletteRequest, db: Session = Depends(get_db)):
    """Model 3 CIELAB Color Harmony Matcher."""
    return ai_fit_controller.get_color_palette(req, db=db)


@legacy_router.post("/vip-styling", response_model=FullStylingResponse)
async def legacy_vip_styling(req: FullStylingRequest, db: Session = Depends(get_db)):
    """VIP Styling Consultation."""
    return await ai_fit_controller.run_vip_styling(db, req)
