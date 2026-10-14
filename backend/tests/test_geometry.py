"""
Unit tests for Computer Vision Silhouette Geometry & Mathematical Calculations.
"""
import pytest
import numpy as np
from ai_models.measurement.feature_extractor import SilhouetteFeatureExtractor
from ai_models.exceptions import InvalidSilhouetteException


def test_ramanujan_circumference_circle():
    """For a circle (a=b=r), circumference should equal 2*pi*r."""
    r = 10.0
    expected = 2.0 * np.pi * r
    calculated = SilhouetteFeatureExtractor.ramanujan_circumference(2 * r, 2 * r)
    assert pytest.approx(expected, rel=1e-3) == calculated


def test_ramanujan_circumference_ellipse():
    """For an ellipse with a=10, b=5, Ramanujan formula should be highly accurate (~48.44 cm)."""
    calculated = SilhouetteFeatureExtractor.ramanujan_circumference(20.0, 10.0)
    assert 48.0 < calculated < 49.0


def test_empty_mask_exception():
    """Empty or null mask must raise InvalidSilhouetteException."""
    empty_mask = np.zeros((100, 100), dtype=np.uint8)
    with pytest.raises(InvalidSilhouetteException):
        SilhouetteFeatureExtractor.get_mask_bounds(empty_mask)


def test_synthetic_mask_feature_extraction():
    """Valid rectangular synthetic mask should be extracted cleanly."""
    mask = np.zeros((500, 300), dtype=np.uint8)
    # Draw body silhouette (100 to 450 y, 100 to 200 x)
    mask[100:450, 100:200] = 255

    extractor = SilhouetteFeatureExtractor()
    features = extractor.extract_features(
        front_mask=mask,
        side_mask=mask,
        height_cm=175.0,
        weight_kg=70.0,
        gender="male"
    )

    assert "c_chest_ramanujan" in features
    assert "bmi" in features
    assert pytest.approx(features["bmi"], rel=1e-2) == 70.0 / (1.75 ** 2)
    assert features["height_cm"] == 175.0
    assert features["weight_kg"] == 70.0
