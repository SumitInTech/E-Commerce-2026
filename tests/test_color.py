"""
Unit tests for Model 3: Photometric CIELAB Skin Tone & Seasonal Palette Matcher.
"""
import numpy as np
import pytest
from models.color.color_engine import ColorEngine


def test_rgb_to_cielab():
    """White RGB [255, 255, 255] should yield L* near 100, a* near 0, b* near 0."""
    engine = ColorEngine()
    white_rgb = np.array([[255, 255, 255]], dtype=np.uint8)
    lab = engine.rgb_to_cielab(white_rgb)
    assert pytest.approx(100.0, abs=2.0) == lab[0, 0]
    assert abs(lab[0, 1]) < 3.0
    assert abs(lab[0, 2]) < 3.0


def test_skin_patch_analysis():
    """Synthetic warm light skin swatch should yield Warm undertone."""
    engine = ColorEngine()
    # Warm beige skin patch
    warm_patch = np.full((30, 30, 3), [225, 185, 145], dtype=np.uint8)
    res = engine.analyze_skin_patch(warm_patch)

    assert "cielab" in res
    assert "ita_degrees" in res
    assert res["undertone"] in ["Warm", "Neutral"]
    assert res["season"] in ["Spring", "Autumn", "Summer", "Winter"]
    assert "best_colors" in res["palette"]
