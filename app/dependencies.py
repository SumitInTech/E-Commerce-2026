"""
Dependency injection provider for application singletons and services.
"""
from typing import Optional
from models.measurement.regressor import BodyMeasurementRegressor
from models.fit.fit_engine import FitEngine
from models.color.color_engine import ColorEngine
from services.rag_service import RAGService


_regressor_instance: Optional[BodyMeasurementRegressor] = None
_fit_engine_instance: Optional[FitEngine] = None
_color_engine_instance: Optional[ColorEngine] = None
_rag_service_instance: Optional[RAGService] = None


def get_regressor() -> BodyMeasurementRegressor:
    global _regressor_instance
    if _regressor_instance is None:
        _regressor_instance = BodyMeasurementRegressor()
    return _regressor_instance


def get_fit_engine() -> FitEngine:
    global _fit_engine_instance
    if _fit_engine_instance is None:
        _fit_engine_instance = FitEngine()
    return _fit_engine_instance


def get_color_engine() -> ColorEngine:
    global _color_engine_instance
    if _color_engine_instance is None:
        _color_engine_instance = ColorEngine()
    return _color_engine_instance


def get_rag_service() -> RAGService:
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
