"""
Model 3: Photometric CIELAB Skin-Tone & Color Palette Matcher.
Transforms RGB patches to CIE L*a*b* color space, applies K-Means clustering,
computes Individual Typology Angle (ITA), and maps to seasonal color palettes.
"""
from typing import Dict, Any, List, Tuple
import numpy as np
import cv2
from sklearn.cluster import KMeans


SEASONAL_PALETTES = {
    "Spring": {
        "description": "Warm & Light: Bright, clear colors with yellow/golden undertones.",
        "best_colors": ["#FF7F50", "#FFA07A", "#98FB98", "#FFF8DC", "#FFD700", "#40E0D0"],
        "color_names": ["Coral", "Light Salmon", "Pale Green", "Cornsilk", "Gold", "Turquoise"],
        "avoid_colors": ["#000000", "#708090", "#800080"],
        "styling_tips": "Opt for fresh, warm-toned neutrals and vibrant warm accents. Avoid harsh black."
    },
    "Summer": {
        "description": "Cool & Light: Soft, muted pastels with blue/rose undertones.",
        "best_colors": ["#E6E6FA", "#B0E0E6", "#778899", "#FFB6C1", "#F0FFFF", "#4682B4"],
        "color_names": ["Lavender", "Powder Blue", "Light Slate Gray", "Light Pink", "Azure", "Steel Blue"],
        "avoid_colors": ["#FFA500", "#8B4513", "#FF4500"],
        "styling_tips": "Delicate jewel tones and soft heathered hues accentuate cool undertones."
    },
    "Autumn": {
        "description": "Warm & Deep: Earthy, rich, and golden-spiced tones.",
        "best_colors": ["#B22222", "#D2691E", "#556B2F", "#DAA520", "#3E2723", "#C04000"],
        "color_names": ["Firebrick", "Chocolate", "Dark Olive Green", "Goldenrod", "Espresso", "Mahogany"],
        "avoid_colors": ["#FF1493", "#00FFFF", "#E0FFFF"],
        "styling_tips": "Rich organic textures, burnt oranges, and warm olive enhance natural warmth."
    },
    "Winter": {
        "description": "Cool & Vivid: High contrast, striking icy tones and deep saturated hues.",
        "best_colors": ["#0047AB", "#50C878", "#9B111E", "#000000", "#FFFFFF", "#800020"],
        "color_names": ["Cobalt Blue", "Emerald Green", "Ruby Red", "Jet Black", "Crisp White", "Burgundy"],
        "avoid_colors": ["#F5F5DC", "#D2B48C", "#DAA520"],
        "styling_tips": "High contrast pairings (pure black & white) and bold jewel tones look striking."
    }
}


class ColorEngine:
    """
    Computes skin pigmentation metrics and seasonal color palette recommendations.
    """

    @staticmethod
    def rgb_to_cielab(rgb_pixels: np.ndarray) -> np.ndarray:
        """
        Converts RGB pixel array [N, 3] in range [0, 255] to standard CIE L*a*b*.
        Returns array [N, 3] with L* in [0, 100], a* in [-128, 127], b* in [-128, 127].
        """
        # Reshape to 1 x N x 3 for OpenCV
        pixels_img = rgb_pixels.reshape((1, -1, 3)).astype(np.uint8)
        # OpenCV converts RGB to Lab where L: 0-255, a: 0-255, b: 0-255
        lab_cv = cv2.cvtColor(pixels_img, cv2.COLOR_RGB2LAB).reshape((-1, 3)).astype(np.float32)

        # Rescale to standard scientific CIELAB: L* in [0, 100], a* and b* centered around 0
        L_star = lab_cv[:, 0] * (100.0 / 255.0)
        a_star = lab_cv[:, 1] - 128.0
        b_star = lab_cv[:, 2] - 128.0

        return np.column_stack([L_star, a_star, b_star])

    @staticmethod
    def compute_ita(L_star: float, b_star: float) -> float:
        """
        Individual Typology Angle:
        ITA = arctan((L* - 50) / b*) * (180 / π)
        """
        if abs(b_star) < 1e-5:
            b_star = 1e-5
        ita_rad = np.arctan((L_star - 50.0) / b_star)
        return float(np.degrees(ita_rad))

    @staticmethod
    def classify_ita_category(ita: float) -> str:
        if ita > 55.0:
            return "Very Light"
        elif ita > 41.0:
            return "Light"
        elif ita > 28.0:
            return "Intermediate"
        elif ita > 10.0:
            return "Tan / Olive"
        elif ita > -30.0:
            return "Brown"
        else:
            return "Dark"

    def analyze_skin_patch(self, rgb_image: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes an RGB skin crop or image patch.
        Uses K-Means clustering (k=3) to extract the dominant dermal centroid.
        """
        if rgb_image is None or rgb_image.size == 0:
            raise ValueError("Provided image is empty or invalid.")

        pixels = rgb_image.reshape((-1, 3)).astype(np.float32)

        # Filter out extreme shadows (too dark) or specular highlights (too bright)
        brightness = np.mean(pixels, axis=1)
        valid_mask = (brightness > 35) & (brightness < 240)
        filtered_pixels = pixels[valid_mask]

        if len(filtered_pixels) < 50:
            filtered_pixels = pixels  # Fallback to all pixels if crop is small

        # Subsample if large to maintain <5ms latency
        if len(filtered_pixels) > 5000:
            indices = np.random.choice(len(filtered_pixels), 5000, replace=False)
            filtered_pixels = filtered_pixels[indices]

        # Convert to CIELAB
        lab_pixels = self.rgb_to_cielab(filtered_pixels)

        # Check unique colors to prevent warnings on synthetic/flat swatches
        unique_colors = np.unique(lab_pixels, axis=0)
        n_clusters = min(3, len(unique_colors))

        if n_clusters <= 1:
            dominant_lab = np.mean(lab_pixels, axis=0)
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=3)
            kmeans.fit(lab_pixels)
            labels, counts = np.unique(kmeans.labels_, return_counts=True)
            dominant_idx = labels[np.argmax(counts)]
            dominant_lab = kmeans.cluster_centers_[dominant_idx]

        L_star, a_star, b_star = dominant_lab[0], dominant_lab[1], dominant_lab[2]
        ita = self.compute_ita(L_star, b_star)
        ita_category = self.classify_ita_category(ita)

        # Determine Undertone
        if b_star > 1.15 * a_star:
            undertone = "Warm"
        elif a_star > b_star or b_star < 8.0:
            undertone = "Cool"
        else:
            undertone = "Neutral"

        # Determine Season
        if undertone == "Warm":
            season = "Spring" if L_star >= 60.0 else "Autumn"
        elif undertone == "Cool":
            season = "Summer" if L_star >= 60.0 else "Winter"
        else:
            # Neutral: classify by lightness
            season = "Spring" if L_star >= 65.0 else "Autumn"

        palette_info = SEASONAL_PALETTES[season]

        return {
            "cielab": {
                "L_star": round(float(L_star), 2),
                "a_star": round(float(a_star), 2),
                "b_star": round(float(b_star), 2)
            },
            "ita_degrees": round(float(ita), 1),
            "ita_category": ita_category,
            "undertone": undertone,
            "season": season,
            "palette": palette_info
        }
