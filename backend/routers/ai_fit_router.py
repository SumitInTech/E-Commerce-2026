"""
AI Fit & Style Service Router.
Exposes Model 1 (Anthropometric Regressor), Model 2 (Garment Fit Engine),
Model 3 (Skin-Tone Color Harmonies), and the combined VIP Styling Consultation.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.ai_fit import (
    BodyMeasurementPredictRequest, BodyMeasurementResponse,
    GarmentFitCheckRequest, GarmentFitResponse,
    SkinTonePaletteRequest, SkinTonePaletteResponse,
    FullStylingRequest, FullStylingResponse
)
from backend.services.ai_fit_service import AIFitService

router = APIRouter(prefix="/ai-fit", tags=["6. AI Fit & Style Service"])


@router.post("/predict-measurements", response_model=BodyMeasurementResponse)
def predict_measurements(req: BodyMeasurementPredictRequest):
    """
    Model 1: Anthropometric Measurement Regressor.
    Predicts 3D chest, waist, and hip circumferences from height/weight biometrics
    or uploaded front/side silhouette masks.
    """
    return AIFitService.predict_measurements(req)


@router.post("/evaluate-garment-fit", response_model=GarmentFitResponse)
def evaluate_garment_fit(req: GarmentFitCheckRequest, db: Session = Depends(get_db)):
    """
    Model 2: Garment Fit & Kinematic Sizing Engine.
    Evaluates body circumferences against real catalog product size charts,
    calculates kinematic ease, detects return-risk, and recommends optimal size.
    """
    return AIFitService.evaluate_garment_fit(db, req)


@router.post("/color-palette", response_model=SkinTonePaletteResponse)
def match_color_palette(req: SkinTonePaletteRequest, db: Session = Depends(get_db)):
    """
    Model 3: CIELAB Photometric Skin-Tone & Color Palette Matcher.
    Calculates Individual Typology Angle (ITA) and returns tailored seasonal color harmonies.
    """
    return AIFitService.match_skin_tone_and_palette(db, req)


@router.post("/vip-styling", response_model=FullStylingResponse)
async def vip_styling(req: FullStylingRequest, db: Session = Depends(get_db)):
    """
    VIP Multi-Model Pipeline:
    Executes Model 1 -> Model 2 -> Model 3 -> Model 4 concurrently for an end-to-end luxury styling consultation.
    """
    return await AIFitService.run_full_styling(db, req)
