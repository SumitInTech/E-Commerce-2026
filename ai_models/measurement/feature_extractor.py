"""
Anthropometric Silhouette Geometric Feature Extractor.
Extracts calibrated anatomical cross-sections, Ramanujan elliptic circumferences,
and morphological indicators from dual-view silhouette masks or biomechanical priors.
"""
from typing import Dict, Any, Tuple, Optional
import numpy as np
import cv2

from ai_models.exceptions import InvalidSilhouetteException


class SilhouetteFeatureExtractor:
    """
    Extracts geometric and calibrated anthropometric features from 
    front and lateral binary masks or biomechanical priors.
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

    @classmethod
    def fill_silhouette_holes(cls, mask: np.ndarray) -> np.ndarray:
        """Fills internal holes and bridges wireframe hollow silhouettes."""
        if mask is None or mask.size == 0:
            return mask
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(mask)
        if contours:
            cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
        return filled

    @staticmethod
    def measure_slice_width(mask: np.ndarray, y_level: int, window: int = 11) -> float:
        """
        Measures horizontal width of silhouette around y_level with median smoothing.
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
        Computes perimeter of an ellipse using Ramanujan's First Approximation:
        C ≈ π [ 3(a + b) - sqrt((3a + b)(a + 3b)) ]
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
        Extracts calibrated anthropometric features from dual masks + demographic metadata.
        """
        front_mask = self.fill_silhouette_holes(front_mask)
        side_mask = self.fill_silhouette_holes(side_mask)

        y_min_front, y_max_front, h_front_px = self.get_mask_bounds(front_mask)
        y_min_side, y_max_side, h_side_px = self.get_mask_bounds(side_mask)

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

        # Biomechanical sanity guards against hollow slices or neck gaps:
        if calibrated_widths["shoulder"] < 18.0:
            if calibrated_widths["chest"] > 20.0:
                calibrated_widths["shoulder"] = calibrated_widths["chest"] * 0.72
            else:
                calibrated_widths["shoulder"] = height_cm * 0.20

        if calibrated_widths["chest"] < 20.0:
            if calibrated_widths["waist"] > 20.0:
                calibrated_widths["chest"] = max(24.0, calibrated_widths["waist"] * 0.95)
            else:
                calibrated_widths["chest"] = height_cm * 0.22

        if calibrated_depths["chest"] < 10.0 or calibrated_depths["chest"] > 45.0:
            calibrated_depths["chest"] = max(14.0, min(36.0, calibrated_widths["chest"] * 0.55))

        c_chest = self.ramanujan_circumference(calibrated_widths["chest"], calibrated_depths["chest"])
        c_waist = self.ramanujan_circumference(calibrated_widths["waist"], calibrated_depths["waist"])
        c_hip = self.ramanujan_circumference(calibrated_widths["hip"], calibrated_depths["hip"])

        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2) if height_m > 0 else 0.0
        ponderal_index = weight_kg / (height_m ** 3) if height_m > 0 else 0.0
        gender_code = 1.0 if str(gender).strip().lower() in ["male", "m", "1"] else 0.0

        waist_to_hip_ratio = float(np.clip(
            calibrated_widths["waist"] / calibrated_widths["hip"]
            if calibrated_widths["hip"] > 0 else 1.0,
            0.60, 1.40
        ))
        chest_to_waist_ratio = float(np.clip(
            calibrated_widths["chest"] / calibrated_widths["waist"]
            if calibrated_widths["waist"] > 0 else 1.0,
            0.60, 1.50
        ))

        return {
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

    def estimate_features_from_biometrics(
        self,
        height_cm: float,
        weight_kg: float,
        gender: str
    ) -> Dict[str, float]:
        """
        Instant anthropometric feature synthesizer when raw photo masks are not uploaded.
        Derived from statistical anthropometry regression distributions.
        """
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2) if height_m > 0 else 22.0
        ponderal_index = weight_kg / (height_m ** 3) if height_m > 0 else 12.5
        is_male = str(gender).strip().lower() in ["male", "m", "1"]
        gender_code = 1.0 if is_male else 0.0

        # Anthropometric statistical basis
        scale = np.sqrt(weight_kg / 70.0) * (height_cm / 175.0)

        if is_male:
            front_chest_w = 31.0 * scale
            side_chest_d = 23.5 * scale
            front_waist_w = 27.5 * scale
            side_waist_d = 22.0 * scale
            front_hip_w = 32.0 * scale
            side_hip_d = 23.0 * scale
            front_shoulder_w = 44.0 * (height_cm / 175.0)
            front_thigh_w = 17.5 * scale
            front_calf_w = 11.5 * scale
        else:
            front_chest_w = 28.5 * scale
            side_chest_d = 21.5 * scale
            front_waist_w = 25.0 * scale
            side_waist_d = 20.0 * scale
            front_hip_w = 34.0 * scale
            side_hip_d = 24.5 * scale
            front_shoulder_w = 39.0 * (height_cm / 165.0)
            front_thigh_w = 18.5 * scale
            front_calf_w = 11.0 * scale

        c_chest = self.ramanujan_circumference(front_chest_w, side_chest_d)
        c_waist = self.ramanujan_circumference(front_waist_w, side_waist_d)
        c_hip = self.ramanujan_circumference(front_hip_w, side_hip_d)

        waist_to_hip_ratio = float(np.clip(front_waist_w / front_hip_w, 0.65, 1.10))
        chest_to_waist_ratio = float(np.clip(front_chest_w / front_waist_w, 0.90, 1.45))

        return {
            "front_chest_w": front_chest_w,
            "side_chest_d": side_chest_d,
            "c_chest_ramanujan": c_chest,
            "front_waist_w": front_waist_w,
            "side_waist_d": side_waist_d,
            "c_waist_ramanujan": c_waist,
            "front_hip_w": front_hip_w,
            "side_hip_d": side_hip_d,
            "c_hip_ramanujan": c_hip,
            "front_shoulder_w": front_shoulder_w,
            "front_thigh_w": front_thigh_w,
            "front_calf_w": front_calf_w,
            "height_cm": float(height_cm),
            "weight_kg": float(weight_kg),
            "bmi": float(bmi),
            "ponderal_index": float(ponderal_index),
            "gender_code": gender_code,
            "waist_to_hip_ratio": float(waist_to_hip_ratio),
            "chest_to_waist_ratio": float(chest_to_waist_ratio),
        }
