"""
AI Fit & Style HTTP Controller.
Coordinates requests for 3D body measurements, garment ease analysis, color palettes, and VIP styling.
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.ai_fit.services.ai_fit_service import ai_fit_service
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


class AIFitController:
    @staticmethod
    def estimate_measurements(db: Optional[Session], req: BodyScanRequest) -> BodyMeasurementResponse:
        try:
            data = ai_fit_service.estimate_body_measurements(db, req)
            return BodyMeasurementResponse(**data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Measurement error: {str(e)}")

    @staticmethod
    def get_fit_advice(req: FitAdviceRequest, db: Optional[Session] = None) -> FitAdviceResponse:
        try:
            data = ai_fit_service.calculate_fit_recommendation(req, db=db)
            return FitAdviceResponse(**data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Fit calculation error: {str(e)}")

    @staticmethod
    def get_color_palette(req: ColorPaletteRequest, db: Optional[Session] = None) -> ColorPaletteResponse:
        try:
            data = ai_fit_service.match_color_palette(req, db=db)
            return ColorPaletteResponse(**data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Color matching error: {str(e)}")

    @staticmethod
    async def run_vip_styling(db: Session, req: FullStylingRequest) -> FullStylingResponse:
        try:
            data = await ai_fit_service.run_full_styling(db, req)
            return FullStylingResponse(**data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Styling consultation error: {str(e)}")


ai_fit_controller = AIFitController()
