"""
Unit tests for Model 1: Body Measurement Regressor Inference.
"""
import os
import cv2
import pytest
from ai_models.measurement.regressor import BodyMeasurementRegressor


def test_regressor_loads_artifact():
    """Regressor should load serialized weights and metadata."""
    regressor = BodyMeasurementRegressor()
    assert regressor.pipeline is not None
    assert "chest" in regressor.targets
    assert "waist" in regressor.targets
    assert "hip" in regressor.targets


def test_regressor_prediction_bounds():
    """Predictions on real sample from train should fall within realistic anatomical limits."""
    regressor = BodyMeasurementRegressor()
    sample_file = "001f3a88501980a5eca6f6346a0ca8d9.png"
    front_path = os.path.join("train/train/mask", sample_file)
    side_path = os.path.join("train/train/mask_left", sample_file)

    if not os.path.exists(front_path):
        pytest.skip("Dataset sample not found.")

    m1 = cv2.imread(front_path, cv2.IMREAD_GRAYSCALE)
    m2 = cv2.imread(side_path, cv2.IMREAD_GRAYSCALE)

    res = regressor.predict_from_masks(
        front_mask=m1,
        side_mask=m2,
        height_cm=160.0,
        weight_kg=92.4,
        gender="female"
    )

    preds = res["predictions"]
    # Physiological sanity bounds: 60 cm to 150 cm for adult circumferences
    assert 60.0 <= preds["chest_cm"] <= 150.0
    assert 50.0 <= preds["waist_cm"] <= 150.0
    assert 60.0 <= preds["hip_cm"] <= 160.0
