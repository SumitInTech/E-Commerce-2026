"""
Unit tests for Model 2: Garment Fit & Kinematic Ease Engine.
"""
import pytest
from ai_models.fit.fit_engine import FitEngine, FitCategory


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
    """Body with chest 96 should recommend Medium in standard size chart."""
    engine = FitEngine()
    body = {"chest": 96.0, "waist": 80.0, "hip": 100.0}
    res = engine.recommend_best_size(body)
    assert res["recommended_size"] in ["M", "L"]


def test_fit_stretch_kinematics_and_size_l():
    """
    Validates user's real curl test case:
    Body: 99.5 chest, 89.2 waist, 99.4 hip
    Garment: 102 chest, 92 waist, 104 hip
    Stretch: 0.15 (15%)
    Must yield Fit (not Large), 2.5cm primary ease, and Size L recommendation.
    """
    engine = FitEngine()
    body = {"chest": 99.5, "waist": 89.2, "hip": 99.4}
    garment = {"chest": 102.0, "waist": 92.0, "hip": 104.0}
    res = engine.evaluate_garment_fit(body, garment, fabric_stretch=0.15)
    assert res["fit_category"] == FitCategory.FIT.value
    assert res["primary_ease_cm"] == 2.5
    assert res["primary_dimension"] == "chest"
    assert res["weighted_average_ease_cm"] == 3.0
    assert res["ease_breakdown"]["chest"]["stretch_reserve_cm"] == 15.3

    best = engine.recommend_best_size(body, fabric_stretch=0.15)
    assert best["recommended_size"] == "L"


def test_three_garment_progression_small_fit_large():
    """
    Validates user's three sequential tests on body 99.5 / 89.2 / 99.4 with 15% stretch:
    1. Smaller garment (96/86/96): Chest ease -3.5cm -> Small (negative ease exceeds -1.5cm comfort limit)
    2. Closer garment (102/92/104): Chest ease +2.5cm -> Fit (tailored ergonomic fit)
    3. Roomier garment (112/104/116): Chest ease +12.5cm -> Large (loose fit)
    """
    engine = FitEngine()
    body = {"chest": 99.5, "waist": 89.2, "hip": 99.4}

    # 1. Smaller
    res_small = engine.evaluate_garment_fit(body, {"chest": 96.0, "waist": 86.0, "hip": 96.0}, fabric_stretch=0.15)
    assert res_small["fit_category"] == FitCategory.SMALL.value
    assert res_small["primary_ease_cm"] == -3.5

    # 2. Closer
    res_fit = engine.evaluate_garment_fit(body, {"chest": 102.0, "waist": 92.0, "hip": 104.0}, fabric_stretch=0.15)
    assert res_fit["fit_category"] == FitCategory.FIT.value
    assert res_fit["primary_ease_cm"] == 2.5

    # 3. Roomier
    res_large = engine.evaluate_garment_fit(body, {"chest": 112.0, "waist": 104.0, "hip": 116.0}, fabric_stretch=0.15)
    assert res_large["fit_category"] == FitCategory.LARGE.value
    assert res_large["primary_ease_cm"] == 12.5

    # 4. Garment size identification
    assert engine.identify_garment_size_label({"chest": 112.0, "waist": 104.0, "hip": 116.0}) == "XL"
    assert engine.identify_garment_size_label({"chest": 102.0, "waist": 92.0, "hip": 104.0}) == "L"


