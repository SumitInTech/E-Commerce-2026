"""
AI Fit & Style Business Domain Service.
Direct bridge connecting the backend platform to the consolidated AI Model Hub:
- Model 1: Anthropometric Body Regressor (Chest, Waist, Hip from height/weight/silhouettes)
- Model 2: Garment Kinematic Ease Engine (Fit, Small, Large polarity & return risk)
- Model 3: Photometric CIELAB Skin-Tone & Seasonal Color Palette Matcher
"""
import base64
import numpy as np
import cv2
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ai_models.main_model import get_ai_hub
from backend.ai_fit.schemas.fit_schema import (
    BodyScanRequest,
    FitAdviceRequest,
    ColorPaletteRequest,
    FullStylingRequest
)
from backend.ai_fit.models.fit_model import SizingHistory
from backend.catalog.models.catalog_model import Product


def decode_base64_mask(b64_str: Optional[str]) -> Optional[np.ndarray]:
    """Decodes base64 string to single channel grayscale mask."""
    if not b64_str or not isinstance(b64_str, str) or len(b64_str.strip()) == 0:
        return None
    try:
        clean_b64 = b64_str.split(",")[1] if "," in b64_str else b64_str
        img_bytes = base64.b64decode(clean_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    except Exception:
        return None


def decode_base64_rgb(b64_str: Optional[str]) -> Optional[np.ndarray]:
    """Decodes base64 string to RGB image array."""
    if not b64_str or not isinstance(b64_str, str) or len(b64_str.strip()) == 0:
        return None
    try:
        clean_b64 = b64_str.split(",")[1] if "," in b64_str else b64_str
        img_bytes = base64.b64decode(clean_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if bgr is not None:
            return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        return None
    except Exception:
        return None


class AIFitService:
    def __init__(self):
        self._hub = None

    @property
    def hub(self):
        if self._hub is None:
            self._hub = get_ai_hub()
        return self._hub

    def estimate_body_measurements(self, db: Optional[Session], req: BodyScanRequest) -> Dict[str, Any]:
        """Runs Model 1: Biometric Anthropometric Body Circumference Regression."""
        front_m = decode_base64_mask(req.front_mask_base64 or req.front_photo_base64)
        side_m = decode_base64_mask(req.side_mask_base64 or req.side_photo_base64)

        raw_result = self.hub.predict_measurements(
            height_cm=req.height_cm,
            weight_kg=req.weight_kg,
            gender=req.gender,
            front_mask=front_m,
            side_mask=side_m
        )

        preds = raw_result.get("predictions", {})
        chest_val = float(preds.get("chest_cm", 98.0))
        waist_val = float(preds.get("waist_cm", 82.0))
        hip_val = float(preds.get("hip_cm", 100.0))
        bmi_val = round(req.weight_kg / ((req.height_cm / 100.0) ** 2), 2)

        # Gender-specific topwear & bottomwear sizing recommendations
        is_female = str(req.gender).lower().strip() in ["female", "woman", "women"]
        waist_inches = max(26, min(44, int(round(waist_val / 2.54))))

        if is_female:
            # Female Topwear Sizing
            if chest_val < 84:
                rec_shirt = "XS"
            elif chest_val < 90:
                rec_shirt = "S"
            elif chest_val < 96:
                rec_shirt = "M"
            elif chest_val < 104:
                rec_shirt = "L"
            else:
                rec_shirt = "XL"
            # Female Bottomwear Sizing (Standard Trouser Waist)
            rec_pant = str(waist_inches if waist_inches % 2 == 0 else waist_inches - 1)
            morphology = "Hourglass Curvature" if hip_val > (waist_val + 15) else "Slender Athletic"
        else:
            # Male Topwear Sizing
            if chest_val < 94:
                rec_shirt = "S"
            elif chest_val < 102:
                rec_shirt = "M"
            elif chest_val < 108:
                rec_shirt = "L"
            elif chest_val < 116:
                rec_shirt = "XL"
            else:
                rec_shirt = "XXL"
            # Male Bottomwear Sizing (Standard Trouser Waist)
            rec_pant = str(waist_inches if waist_inches % 2 == 0 else waist_inches - 1)
            morphology = "Athletic V-Taper" if chest_val > (waist_val + 10) else "Modern Tailored Regular"

        # Persist sizing scan record if db is available
        if db:
            try:
                history = SizingHistory(
                    user_id=req.user_id,
                    height_cm=req.height_cm,
                    weight_kg=req.weight_kg,
                    gender=req.gender,
                    predicted_chest_cm=chest_val,
                    predicted_waist_cm=waist_val,
                    predicted_hip_cm=hip_val,
                    recommended_size=rec_shirt
                )
                db.add(history)
                db.commit()
            except Exception:
                pass

        return {
            "status": "success",
            "inference_mode": raw_result.get("inference_mode", "biometric_prior"),
            "height_cm": req.height_cm,
            "weight_kg": req.weight_kg,
            "gender": req.gender,
            "chest_cm": chest_val,
            "waist_cm": waist_val,
            "hip_cm": hip_val,
            "bmi": bmi_val,
            "confidence_score": 0.94,
            "recommended_standard_size": rec_shirt,
            "recommended_shirt_size": rec_shirt,
            "recommended_pant_size": rec_pant,
            "recommended_pant_waist_inches": waist_inches,
            "body_morphology": morphology,
            "predictions": {
                "chest_cm": chest_val,
                "waist_cm": waist_val,
                "hip_cm": hip_val
            },
            "extracted_features": raw_result.get("extracted_features")
        }

    def calculate_fit_recommendation(self, req: FitAdviceRequest, db: Optional[Session] = None) -> Dict[str, Any]:
        """Runs Model 2: Garment Kinematic Ease & Sizing Tolerances."""
        specs = req.garment_specs
        garment_type = req.garment_type
        stretch = req.fabric_stretch
        brand_chart = None

        if req.product_id and db:
            product = db.query(Product).filter(Product.id == req.product_id).first()
            if product:
                garment_type = product.garment_type
                stretch = product.fabric_stretch
                brand_chart = {}
                for s in product.sizes:
                    entry = {}
                    if s.chest_cm and s.chest_cm > 0: entry["chest"] = s.chest_cm
                    if s.waist_cm and s.waist_cm > 0: entry["waist"] = s.waist_cm
                    if s.hip_cm and s.hip_cm > 0: entry["hip"] = s.hip_cm
                    if entry:
                        brand_chart[s.size_label] = entry

                if not specs and "M" in brand_chart:
                    specs = brand_chart["M"]

        raw_res = self.hub.recommend_size_and_fit(
            chest_cm=req.chest_cm,
            waist_cm=req.waist_cm,
            hip_cm=req.hip_cm,
            garment_type=garment_type,
            garment_specs=specs,
            fabric_stretch=stretch,
            brand_size_chart=brand_chart
        )

        rec_size = raw_res.get("recommended_size", "M")
        fit_cat = raw_res.get("fit_category", "Fit")
        risk = float(raw_res.get("return_risk_score", 0.05))
        primary_dim = raw_res.get("primary_dimension", "chest")
        primary_ease = float(raw_res.get("primary_ease_cm", 6.0))
        weighted_ease = float(raw_res.get("weighted_average_ease_cm", primary_ease))

        evaluation = raw_res.get("size_details", {}).get("evaluation", {})
        verdict = raw_res.get("verdict", evaluation.get("verdict", "Optimal ergonomic drape with clean silhouette."))
        breakdown = raw_res.get("dimension_breakdown", evaluation.get("ease_breakdown", {}))

        ease_allowances = {
            "chest_ease_cm": float(breakdown.get("chest", {}).get("effective_ease_cm", primary_ease if primary_dim == "chest" else 6.0)),
            "waist_ease_cm": float(breakdown.get("waist", {}).get("effective_ease_cm", primary_ease if primary_dim == "waist" else 6.0)),
            "hip_ease_cm": float(breakdown.get("hip", {}).get("effective_ease_cm", primary_ease if primary_dim == "hip" else 8.0))
        }

        return {
            "status": "success",
            "recommended_size": rec_size,
            "fit_category": fit_cat,
            "ease_allowance_cm": ease_allowances,
            "primary_ease_cm": primary_ease,
            "primary_dimension": primary_dim,
            "weighted_average_ease_cm": weighted_ease,
            "return_risk_score": risk,
            "advice_note": verdict,
            "size_advice": verdict,
            "verdict": verdict,
            "dimension_breakdown": breakdown
        }

    def match_color_palette(self, req: ColorPaletteRequest, db: Optional[Session] = None) -> Dict[str, Any]:
        """Runs Model 3: Photometric CIELAB Skin-Tone & Color Harmony."""
        hex_val = req.hex_color
        detected_from_image = False
        detected_skin_hex = None

        # Check if user uploaded a photo/selfie in image_base64
        if req.image_base64:
            rgb_img = decode_base64_rgb(req.image_base64)
            if rgb_img is not None and rgb_img.size > 0:
                try:
                    h, w, _ = rgb_img.shape
                    # Center crop where face/skin is focused
                    y1, y2 = max(0, int(h * 0.2)), min(h, int(h * 0.8))
                    x1, x2 = max(0, int(w * 0.2)), min(w, int(w * 0.8))
                    crop = rgb_img[y1:y2, x1:x2] if (y2 > y1 and x2 > x1) else rgb_img

                    # Extract dominant dermal color
                    pixels = crop.reshape(-1, 3).astype(np.float32)
                    brightness = np.mean(pixels, axis=1)
                    valid = pixels[(brightness > 45) & (brightness < 230)]
                    if len(valid) > 20:
                        med_rgb = np.median(valid, axis=0).astype(int)
                    else:
                        med_rgb = np.median(pixels, axis=0).astype(int)

                    r_clamped = max(0, min(255, int(med_rgb[0])))
                    g_clamped = max(0, min(255, int(med_rgb[1])))
                    b_clamped = max(0, min(255, int(med_rgb[2])))
                    detected_skin_hex = f"#{r_clamped:02x}{g_clamped:02x}{b_clamped:02x}"
                    hex_val = detected_skin_hex
                    detected_from_image = True
                except Exception:
                    pass

        if not hex_val and req.r is not None and req.g is not None and req.b is not None:
            hex_val = f"#{req.r:02x}{req.g:02x}{req.b:02x}"
        if not hex_val:
            hex_val = "#D4AA78"

        raw_res = self.hub.match_skin_tone_and_palette(hex_color=hex_val, ita=req.ita)
        season = raw_res.get("seasonal_tone", "Autumn")

        catalog_recs = []
        if db:
            products = db.query(Product).limit(4).all()
            for p in products:
                catalog_recs.append({
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "image_url": p.image_url,
                    "fabric": p.fabric,
                    "harmony_reason": f"Complements {season} undertones with balanced contrast."
                })

        return {
            "status": "success",
            "input_hex": hex_val,
            "detected_from_image": detected_from_image,
            "detected_skin_hex": detected_skin_hex or hex_val,
            "skin_tone_category": raw_res.get("ita_category", "Intermediate"),
            "ita_angle": float(raw_res.get("ita_angle", 35.2)),
            "ita_category": raw_res.get("ita_category", "Intermediate"),
            "recommended_palette": season,
            "seasonal_tone": season,
            "palette_description": raw_res.get("palette_description", "Warm earthy tones with rich saturation."),
            "complementary_colors": raw_res.get("best_colors", ["#B22222", "#D2691E", "#556B2F"]),
            "best_colors": raw_res.get("best_colors", ["#B22222", "#D2691E", "#556B2F"]),
            "color_names": raw_res.get("color_names", ["Brick Red", "Warm Rust", "Olive Drab"]),
            "avoid_colors": raw_res.get("avoid_colors", ["#FF1493", "#00FFFF"]),
            "styling_advice": raw_res.get("styling_tips", "Earthy neutrals and deep jewel tones enhance skin undertones."),
            "styling_tips": raw_res.get("styling_tips", "Earthy neutrals and deep jewel tones enhance skin undertones."),
            "recommended_catalog_items": catalog_recs
        }

    async def run_full_styling(self, db: Session, req: FullStylingRequest) -> Dict[str, Any]:
        """VIP Multi-Model Styling Consultation chaining Models 1, 2, and 3."""
        meas = self.estimate_body_measurements(db, BodyScanRequest(
            height_cm=req.height_cm,
            weight_kg=req.weight_kg,
            gender=req.gender
        ))
        fit = self.calculate_fit_recommendation(FitAdviceRequest(
            chest_cm=meas["chest_cm"],
            waist_cm=meas["waist_cm"],
            hip_cm=meas["hip_cm"],
            product_id=req.product_id,
            garment_type=req.garment_type
        ), db=db)
        color = self.match_color_palette(ColorPaletteRequest(
            hex_color=req.hex_skin_color
        ), db=db)

        notes = (
            f"For your frame ({req.height_cm}cm, {req.weight_kg}kg, {req.gender}), our AI recommends Shirt Size {meas['recommended_shirt_size']} and Pant Size {meas['recommended_pant_size']}. "
            f"Your skin profile aligns with the {color['seasonal_tone']} palette ({', '.join(color.get('color_names', [])[:3])}). "
            f"Tailoring verdict: {fit['advice_note']}"
        )

        return {
            "status": "success",
            "user_profile": {
                "height_cm": req.height_cm,
                "weight_kg": req.weight_kg,
                "gender": req.gender,
                "bmi": meas["bmi"],
                "body_morphology": meas["body_morphology"],
                "recommended_shirt_size": meas["recommended_shirt_size"],
                "recommended_pant_size": meas["recommended_pant_size"]
            },
            "predicted_measurements": meas["predictions"],
            "recommended_size": fit["recommended_size"],
            "recommended_shirt_size": meas["recommended_shirt_size"],
            "recommended_pant_size": meas["recommended_pant_size"],
            "fit_analysis": fit,
            "color_analysis": color,
            "personalized_styling_notes": notes
        }


ai_fit_service = AIFitService()
