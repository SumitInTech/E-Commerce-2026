"""
Unit tests for SilhouetteValidator and defensive mask preprocessing.
"""
import numpy as np
import cv2
import pytest
from ai_models.measurement.silhouette_validator import SilhouetteValidator, SilhouetteValidationResult


def test_clean_binary_silhouette():
    """Verifies that a valid binary mask passes validation."""
    mask = np.zeros((1000, 400), dtype=np.uint8)
    mask[150:850, 100:300] = 255
    res = SilhouetteValidator.analyze_mask(mask)
    assert res.is_valid is True
    assert res.is_inverted is False
    assert res.mask is not None
    assert res.metrics["binarity_ratio"] >= 0.95


def test_inverted_silhouette_auto_correction():
    """Verifies that a negative mask (black body, white background) is detected and auto-inverted."""
    mask = np.full((1000, 400), 255, dtype=np.uint8)
    mask[150:850, 100:300] = 0  # Black body on white background
    res = SilhouetteValidator.analyze_mask(mask)
    assert res.is_valid is True
    assert res.is_inverted is True
    # The cleaned mask should have white body and black background
    assert np.mean(res.mask[0:50, :]) < 10.0  # background is black
    assert np.mean(res.mask[200:800, 150:250]) > 240.0  # body is white


def test_raw_unsegmented_photo_rejected():
    """Verifies that an unsegmented camera photo with light background is rejected as a binary mask."""
    photo = np.full((1000, 500), 240, dtype=np.uint8)  # Light room wall
    photo[150:850, 150:350] = 75  # Darker person
    res = SilhouetteValidator.analyze_mask(photo)
    assert res.is_valid is False
    assert "unsegmented photograph" in res.rejection_reason.lower() or "not a valid binary" in res.rejection_reason.lower()


def test_photo_heuristic_segmentation():
    """Verifies that a high-contrast photo can be segmented into a valid silhouette mask."""
    photo = np.full((1000, 500), 240, dtype=np.uint8)
    photo[150:850, 150:350] = 60
    seg_res = SilhouetteValidator.attempt_segmentation(photo)
    assert seg_res.is_valid is True
    assert seg_res.was_segmented is True
    assert seg_res.mask is not None


def test_empty_image_validation():
    """Verifies graceful handling of empty or tiny image matrices."""
    empty = np.zeros((10, 10), dtype=np.uint8)
    res = SilhouetteValidator.analyze_mask(empty)
    assert res.is_valid is False
    assert "resolution too small" in res.rejection_reason.lower()
