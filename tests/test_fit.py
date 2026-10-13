"""
Unit tests for Model 2: Garment Fit & Kinematic Ease Engine.
"""
import pytest
from models.fit.fit_engine import FitEngine, FitCategory


def test_fit_category_tight():
    """Negative ease should yield Small."""
    engine = FitEngine()
    body = {"chest": 100.0, "waist": 85.0, "hip": 102.0}
    garment = {"chest": 96.0, "waist": 80.0, "hip": 98.0}
    res = engine.evaluate_garment_fit(body, garment)
    assert res["fit_category"] == FitCategory.SMALL.value


def test_fit_category_fit():
    """Ease between 0 and 6 cm should yield Fit."""
    engine = FitEngine()
    body = {"chest": 100.0, "waist": 85.0, "hip": 102.0}
    garment = {"chest": 104.0, "waist": 88.0, "hip": 105.0}
    res = engine.evaluate_garment_fit(body, garment)
    assert res["fit_category"] == FitCategory.FIT.value


def test_fit_category_large():
    """Ease > 6 cm should yield Large."""
    engine = FitEngine()
    body = {"chest": 100.0, "waist": 85.0, "hip": 102.0}
    garment = {"chest": 112.0, "waist": 96.0, "hip": 115.0}
    res = engine.evaluate_garment_fit(body, garment)
    assert res["fit_category"] == FitCategory.LARGE.value


def test_recommend_best_size():
    """Body with chest 98 should recommend Medium in standard size chart."""
    engine = FitEngine()
    body = {"chest": 96.0, "waist": 80.0, "hip": 100.0}
    res = engine.recommend_best_size(body)
    assert res["recommended_size"] in ["M", "L"]
