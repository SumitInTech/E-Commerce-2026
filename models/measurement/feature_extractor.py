"""
Anthropometric Silhouette Geometric Feature Extractor.
Extracts calibrated anatomical cross-sections, Ramanujan elliptic circumferences,
and morphological indicators from dual-view silhouette masks.
"""
from typing import Dict, Any, Tuple, Optional
import numpy as np
import cv2

from core.exceptions import InvalidSilhouetteException


class SilhouetteFeatureExtractor:
    """
    Extracts geometric and calibrated anthropometric features from 
    front and lateral binary masks.
    """

    # Proportional anatomical levels (from head vertex to soles)
    LEVELS = {
        "shoulder": 0.18,
        "chest": 0.28,
        "waist": 0.42,
        "hip": 0.53,
        "thigh": 0.65,
        "calf": 0.82
    }

    @staticmethod
    def get_mask_bounds(mask: np.ndarray) -> Tuple[int, int, int]:
        """
        Locates the vertical bounds of the silhouette.
        Returns: (y_min, y_max, pixel_height)
        """
        if mask is None or mask.size == 0:
            raise InvalidSilhouetteException("Mask array is null or empty.")

        # Ensure single channel grayscale
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        y_indices, _ = np.where(mask > 128)
        if len(y_indices) < 100:
            raise InvalidSilhouetteException("Foreground silhouette is too small or missing.")

        y_min = int(np.min(y_indices))
        y_max = int(np.max(y_indices))
        pixel_height = y_max - y_min

        if pixel_height < 50:
            raise InvalidSilhouetteException(f"Silhouette height too small: {pixel_height}px.")

        return y_min, y_max, pixel_height

    @staticmethod
    def measure_slice_width(mask: np.ndarray, y_level: int, window: int = 5) -> float:
        """
        Measures the horizontal width of the foreground silhouette around y_level.
        Uses a small vertical window median to filter out high-frequency boundary noise.
        """
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        h, w = mask.shape
        widths = []
        half = window // 2

        for y in range(max(0, y_level - half), min(h, y_level + half + 1)):
            x_indices = np.where(mask[y, :] > 128)[0]
            if len(x_indices) > 0:
                widths.append(float(x_indices.max() - x_indices.min()))
            else:
                widths.append(0.0)

        if not widths or max(widths) == 0.0:
            return 0.0

        return float(np.median(widths))

    @staticmethod
    def ramanujan_circumference(width_cm: float, depth_cm: float) -> float:
        """
        Computes the perimeter of an ellipse using Ramanujan's First Approximation:
        C ≈ π [ 3(a + b) - sqrt((3a + b)(a + 3b)) ]
        where a = width_cm / 2 (semi-major) and b = depth_cm / 2 (semi-minor).
        """
        if width_cm <= 0 or depth_cm <= 0:
            return 0.0

        a = width_cm / 2.0
        b = depth_cm / 2.0
        term1 = 3.0 * (a + b)
        term2 = np.sqrt((3.0 * a + b) * (a + 3.0 * b))
        return float(np.pi * (term1 - term2))

    def extract_features(
        self,
        front_mask: np.ndarray,
        side_mask: np.ndarray,
        height_cm: float,
        weight_kg: float,
        gender: str
    ) -> Dict[str, float]:
        """
        Extracts calibrated anthropometric features from front and lateral masks
        combined with user metadata.
        """
        y_min_front, y_max_front, h_front_px = self.get_mask_bounds(front_mask)
        y_min_side, y_max_side, h_side_px = self.get_mask_bounds(side_mask)

        # Scale calibrations (cm / pixel)
        cm_per_px_front = height_cm / float(h_front_px)
        cm_per_px_side = height_cm / float(h_side_px)

        calibrated_widths = {}
        calibrated_depths = {}

        for part, ratio in self.LEVELS.items():
            y_front = int(y_min_front + ratio * h_front_px)
            y_side = int(y_min_side + ratio * h_side_px)

            w_px = self.measure_slice_width(front_mask, y_front)
            d_px = self.measure_slice_width(side_mask, y_side)

            calibrated_widths[part] = w_px * cm_per_px_front
            calibrated_depths[part] = d_px * cm_per_px_side

        # Circumferences via Ramanujan approximation
        c_chest = self.ramanujan_circumference(calibrated_widths["chest"], calibrated_depths["chest"])
        c_waist = self.ramanujan_circumference(calibrated_widths["waist"], calibrated_depths["waist"])
        c_hip = self.ramanujan_circumference(calibrated_widths["hip"], calibrated_depths["hip"])

        # Physiological indicators
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2) if height_m > 0 else 0.0
        ponderal_index = weight_kg / (height_m ** 3) if height_m > 0 else 0.0
        gender_code = 1.0 if str(gender).strip().lower() in ["male", "m", "1"] else 0.0

        # Structural ratios
        waist_to_hip_ratio = (
            calibrated_widths["waist"] / calibrated_widths["hip"]
            if calibrated_widths["hip"] > 0 else 1.0
        )
        chest_to_waist_ratio = (
            calibrated_widths["chest"] / calibrated_widths["waist"]
            if calibrated_widths["waist"] > 0 else 1.0
        )

        features = {
            "front_chest_w": calibrated_widths["chest"],
            "side_chest_d": calibrated_depths["chest"],
            "c_chest_ramanujan": c_chest,
            "front_waist_w": calibrated_widths["waist"],
            "side_waist_d": calibrated_depths["waist"],
            "c_waist_ramanujan": c_waist,
            "front_hip_w": calibrated_widths["hip"],
            "side_hip_d": calibrated_depths["hip"],
            "c_hip_ramanujan": c_hip,
            "front_shoulder_w": calibrated_widths["shoulder"],
            "front_thigh_w": calibrated_widths["thigh"],
            "front_calf_w": calibrated_widths["calf"],
            "height_cm": float(height_cm),
            "weight_kg": float(weight_kg),
            "bmi": float(bmi),
            "ponderal_index": float(ponderal_index),
            "gender_code": gender_code,
            "waist_to_hip_ratio": float(waist_to_hip_ratio),
            "chest_to_waist_ratio": float(chest_to_waist_ratio),
        }

        return features
