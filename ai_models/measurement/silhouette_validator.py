"""
Silhouette Quality Validator & Defensive Mask Pre-processor.
Validates binary silhouette masks, detects and auto-inverts negative masks,
analyzes morphological aspect ratios, and provides robust background-difference
segmentation for natural photographs and sketches.
"""
from typing import Tuple, Optional, Dict, Any
import numpy as np
import cv2


class SilhouetteValidationResult:
    """Encapsulates the assessment and pre-processed mask."""
    def __init__(
        self,
        is_valid: bool,
        mask: Optional[np.ndarray],
        is_inverted: bool = False,
        was_segmented: bool = False,
        rejection_reason: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None
    ):
        self.is_valid = is_valid
        self.mask = mask
        self.is_inverted = is_inverted
        self.was_segmented = was_segmented
        self.rejection_reason = rejection_reason
        self.metrics = metrics or {}


class SilhouetteValidator:
    """
    Defensive analyzer ensuring uploaded images adhere to the binary
    anthropometric silhouette contract required by the geometric feature extractor.
    """

    @staticmethod
    def to_grayscale(img: np.ndarray) -> np.ndarray:
        """Converts an image array to single channel 8-bit grayscale."""
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                # Handle RGBA - blend with black background
                alpha = img[:, :, 3] / 255.0
                gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
                return (gray * alpha).astype(np.uint8)
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @classmethod
    def fill_silhouette_holes(cls, mask: np.ndarray) -> np.ndarray:
        """Fills internal holes and bridges wireframe hollow silhouettes."""
        if mask is None or mask.size == 0:
            return mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(mask)
        if contours:
            cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
        return filled

    @classmethod
    def analyze_mask(cls, img: np.ndarray) -> SilhouetteValidationResult:
        """
        Performs forensic verification of an image mask:
        1. Checks for null/empty arrays.
        2. Measures dual-cluster binarity (verifies BOTH solid foreground and solid background exist).
        3. Rejects natural photographs with continuous gradients to trigger intelligent segmentation.
        4. Detects inverted masks and auto-corrects via cv2.bitwise_not().
        5. Fills internal holes and asserts human aspect ratio bounds.
        """
        if img is None or img.size == 0:
            return SilhouetteValidationResult(
                is_valid=False,
                mask=None,
                rejection_reason="Image array is null or empty."
            )

        gray = cls.to_grayscale(img)
        h, w = gray.shape

        if h < 50 or w < 30:
            return SilhouetteValidationResult(
                is_valid=False,
                mask=None,
                rejection_reason=f"Image resolution too small: {w}x{h}px."
            )

        # Step 1: Detect border background intensity
        border_h = max(2, int(h * 0.04))
        border_w = max(2, int(w * 0.04))
        border_pixels = np.concatenate([
            gray[:border_h, :].ravel(),
            gray[-border_h:, :].ravel(),
            gray[:, :border_w].ravel(),
            gray[:, -border_w:].ravel()
        ])
        mean_border = float(np.mean(border_pixels))
        is_inverted = mean_border > 180.0

        # Step 2: Dual-Cluster Binarity Analysis
        # A true binary mask MUST have both a substantial black cluster AND a substantial white cluster
        total_px = float(gray.size)
        black_ratio = float(np.sum(gray < 35)) / total_px
        white_ratio = float(np.sum(gray > 220)) / total_px
        mid_tones_ratio = float(np.sum((gray >= 35) & (gray <= 220))) / total_px

        # In natural photos with a white background, black_ratio is ~0.001 and mid-tones are > 0.12
        is_true_binary = (
            (black_ratio >= 0.035 and white_ratio >= 0.035) and
            (mid_tones_ratio <= 0.12)
        )

        if not is_true_binary:
            # This is a natural photograph or sketch with continuous tones, NOT a pre-segmented binary mask!
            return SilhouetteValidationResult(
                is_valid=False,
                mask=None,
                is_inverted=is_inverted,
                rejection_reason=(
                    f"Image is an unsegmented photograph/drawing. "
                    f"Black cluster: {black_ratio:.3f}, White cluster: {white_ratio:.3f}, "
                    f"Mid-tones: {mid_tones_ratio:.3f}. Requires foreground segmentation."
                ),
                metrics={
                    "black_ratio": round(black_ratio, 3),
                    "white_ratio": round(white_ratio, 3),
                    "mid_tones": round(mid_tones_ratio, 3)
                }
            )

        # If it is a true binary mask, orient so foreground is 255 (white) and background is 0 (black)
        working_gray = cv2.bitwise_not(gray) if is_inverted else gray.copy()

        # Binarize cleanly
        _, binary = cv2.threshold(working_gray, 128, 255, cv2.THRESH_BINARY)

        # Fill internal holes (e.g. hollow line drawings or clothing patterns)
        filled_binary = cls.fill_silhouette_holes(binary)

        # Step 3: Foreground Bounding Box & Aspect Ratio
        y_indices, x_indices = np.where(filled_binary > 128)
        if len(y_indices) < 100:
            return SilhouetteValidationResult(
                is_valid=False,
                mask=None,
                is_inverted=is_inverted,
                rejection_reason="No human foreground silhouette detected."
            )

        y_min, y_max = int(np.min(y_indices)), int(np.max(y_indices))
        x_min, x_max = int(np.min(x_indices)), int(np.max(x_indices))
        sil_height = y_max - y_min
        sil_width = max(1, x_max - x_min)
        aspect_ratio = float(sil_height) / float(sil_width)

        # Step 4: Foreground Area Fill Ratio
        fg_area = len(y_indices)
        fill_ratio = float(fg_area) / total_px

        # Step 5: Border Bleed
        left_bleed = np.sum(filled_binary[:, :max(1, int(w * 0.02))] > 128) / float(h)
        right_bleed = np.sum(filled_binary[:, -max(1, int(w * 0.02)):] > 128) / float(h)
        top_bleed = np.sum(filled_binary[:max(1, int(h * 0.02)), :] > 128) / float(w)
        total_bleed = (left_bleed + right_bleed + top_bleed) / 3.0

        metrics = {
            "binarity_ratio": round(black_ratio + white_ratio, 3),
            "aspect_ratio": round(aspect_ratio, 2),
            "fill_ratio": round(fill_ratio, 3),
            "border_bleed": round(total_bleed, 3),
            "sil_height": sil_height,
            "sil_width": sil_width
        }

        is_plausible = (
            1.5 <= aspect_ratio <= 7.0 and
            0.03 <= fill_ratio <= 0.65 and
            total_bleed < 0.25
        )

        if is_plausible:
            return SilhouetteValidationResult(
                is_valid=True,
                mask=filled_binary,
                is_inverted=is_inverted,
                was_segmented=False,
                metrics=metrics
            )

        return SilhouetteValidationResult(
            is_valid=False,
            mask=None,
            is_inverted=is_inverted,
            rejection_reason=f"Silhouette geometry out of bounds (aspect_ratio: {aspect_ratio:.2f}, fill: {fill_ratio:.2f}).",
            metrics=metrics
        )

    @classmethod
    def attempt_segmentation(cls, img: np.ndarray) -> SilhouetteValidationResult:
        """
        Segments natural photographs and sketches using adaptive background-difference
        detection, directional morphological bridging, and contour hole filling.
        """
        if img is None or img.size == 0:
            return SilhouetteValidationResult(is_valid=False, mask=None, rejection_reason="Empty image.")

        gray = cls.to_grayscale(img)
        h, w = gray.shape

        # Step 1: Compute robust background estimate from image perimeter
        border_h = max(2, int(h * 0.03))
        border_w = max(2, int(w * 0.03))
        border_pixels = np.concatenate([
            gray[:border_h, :].ravel(),
            gray[-border_h:, :].ravel(),
            gray[:, :border_w].ravel(),
            gray[:, -border_w:].ravel()
        ])
        bg_val = float(np.median(border_pixels))
        bg_std = float(np.std(border_pixels))

        # Step 2: Background difference calculation
        diff = cv2.absdiff(gray, int(bg_val))

        # Adaptive threshold: sensitive enough to capture light skin/shirts (20-25)
        diff_thresh = max(18, min(35, int(bg_std * 3.5)))
        _, fg = cv2.threshold(diff, diff_thresh, 255, cv2.THRESH_BINARY)

        # Step 3: Directional morphological closing
        # Vertical closing bridges neck gaps and head-torso disconnects
        k_v = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 17))
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k_v, iterations=2)

        # Elliptical closing smooths body contour
        k_e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k_e, iterations=2)

        # Step 4: Extract all significant body contours (head, torso, legs)
        contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return SilhouetteValidationResult(is_valid=False, mask=None, rejection_reason="No contours found in photo.")

        min_area = (h * w) * 0.006
        significant_cnts = [c for c in contours if cv2.contourArea(c) >= min_area]

        if not significant_cnts:
            # Fall back to largest contour
            significant_cnts = [max(contours, key=cv2.contourArea)]

        # Draw filled solid body mask
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, significant_cnts, -1, 255, thickness=cv2.FILLED)

        # Final morphological close to solidify any internal breaks
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_e, iterations=2)

        # Step 5: Validate resulting segmented mask
        y_indices, x_indices = np.where(mask > 128)
        if len(y_indices) < 100:
            return SilhouetteValidationResult(is_valid=False, mask=None, rejection_reason="Segmented mask is empty.")

        y_min, y_max = int(np.min(y_indices)), int(np.max(y_indices))
        x_min, x_max = int(np.min(x_indices)), int(np.max(x_indices))
        sil_height = y_max - y_min
        sil_width = max(1, x_max - x_min)
        aspect_ratio = float(sil_height) / float(sil_width)
        fill_ratio = float(len(y_indices)) / float(h * w)

        if 1.4 <= aspect_ratio <= 7.5 and 0.03 <= fill_ratio <= 0.70:
            return SilhouetteValidationResult(
                is_valid=True,
                mask=mask,
                was_segmented=True,
                metrics={
                    "aspect_ratio": round(aspect_ratio, 2),
                    "fill_ratio": round(fill_ratio, 3),
                    "sil_height": sil_height,
                    "sil_width": sil_width
                }
            )

        return SilhouetteValidationResult(
            is_valid=False,
            mask=None,
            rejection_reason=f"Segmented mask aspect ratio ({aspect_ratio:.2f}) or fill ({fill_ratio:.2f}) outside human bounds."
        )
