"""
Model 2: Garment Fit & Kinematic Ease Recommendation Engine.
Analyzes anthropometric ease allowances, textile stretch factors, and garment size charts
to provide deterministic fit classifications (Small, Fit, Large) and optimal size selection.
"""
from typing import Dict, Any, Optional
from enum import Enum


class FitCategory(str, Enum):
    SMALL = "Small"
    FIT = "Fit"
    LARGE = "Large"


STANDARD_SIZE_CHART = {
    "XS": {"chest": 86.0, "waist": 70.0, "hip": 90.0},
    "S": {"chest": 92.0, "waist": 76.0, "hip": 96.0},
    "M": {"chest": 98.0, "waist": 82.0, "hip": 102.0},
    "L": {"chest": 104.0, "waist": 88.0, "hip": 108.0},
    "XL": {"chest": 112.0, "waist": 96.0, "hip": 116.0},
    "XXL": {"chest": 120.0, "waist": 104.0, "hip": 124.0},
}


class FitEngine:
    """
    Computes garment-to-body kinematic ease allowances and determines
    ergonomic fit classification.
    """

    DEFAULT_TOLERANCES = {
        "chest": {"tight_bound": 0.0, "loose_bound": 6.0},
        "waist": {"tight_bound": 1.0, "loose_bound": 5.0},
        "hip": {"tight_bound": 2.0, "loose_bound": 7.0},
    }

    def evaluate_garment_fit(
        self,
        body_measurements: Dict[str, float],
        garment_specs: Dict[str, float],
        fabric_stretch: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluates fit category for a specific garment specification against body measurements.
        
        Args:
            body_measurements: Dict containing 'chest', 'waist', and/or 'hip' in cm.
            garment_specs: Dict containing garment dimensions in cm.
            fabric_stretch: Elastane/spandex stretch factor [0.0 to 0.3].
        """
        ease_breakdown = {}
        category_votes = []

        primary_dim = "chest" if "chest" in body_measurements and "chest" in garment_specs else None
        if not primary_dim:
            # Fallback to first common dimension
            common = set(body_measurements.keys()).intersection(set(garment_specs.keys()))
            if common:
                primary_dim = list(common)[0]

        for dim, body_val in body_measurements.items():
            if dim in garment_specs:
                garment_val = float(garment_specs[dim])
                # Stretch allowance increases effective garment dimension
                effective_garment = garment_val * (1.0 + min(fabric_stretch, 0.3))
                ease = effective_garment - float(body_val)

                tol = self.DEFAULT_TOLERANCES.get(dim, {"tight_bound": 0.0, "loose_bound": 6.0})
                tight_bound = tol["tight_bound"]
                loose_bound = tol["loose_bound"]

                if ease < tight_bound:
                    cat = FitCategory.SMALL
                elif ease <= loose_bound:
                    cat = FitCategory.FIT
                else:
                    cat = FitCategory.LARGE

                ease_breakdown[dim] = {
                    "body_cm": round(float(body_val), 1),
                    "garment_cm": round(float(garment_val), 1),
                    "effective_ease_cm": round(float(ease), 1),
                    "category": cat.value
                }
                category_votes.append(cat)

        # Primary verdict determined by chest ease if available, otherwise majority vote
        if primary_dim and primary_dim in ease_breakdown:
            overall_cat = ease_breakdown[primary_dim]["category"]
            primary_ease = ease_breakdown[primary_dim]["effective_ease_cm"]
        elif category_votes:
            # If any measurement is Small, prioritize Small to prevent tight returns
            if FitCategory.SMALL in category_votes:
                overall_cat = FitCategory.SMALL.value
            elif FitCategory.LARGE in category_votes and FitCategory.FIT not in category_votes:
                overall_cat = FitCategory.LARGE.value
            else:
                overall_cat = FitCategory.FIT.value
            primary_ease = 0.0
        else:
            overall_cat = FitCategory.FIT.value
            primary_ease = 0.0

        verdict_explanations = {
            FitCategory.SMALL.value: f"Garment is too snug (ease: {primary_ease:+.1f} cm). Recommend sizing up for comfort.",
            FitCategory.FIT.value: f"Optimal ergonomic drape (ease: {primary_ease:+.1f} cm). True to size.",
            FitCategory.LARGE.value: f"Garment fits loose / relaxed (ease: {primary_ease:+.1f} cm). Recommend sizing down if tailored look is desired."
        }

        return {
            "fit_category": overall_cat,
            "primary_ease_cm": primary_ease,
            "verdict": verdict_explanations.get(overall_cat, "Fit evaluated."),
            "ease_breakdown": ease_breakdown
        }

    def recommend_best_size(
        self,
        body_measurements: Dict[str, float],
        size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        fabric_stretch: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluates a full size chart to determine the optimal size.
        """
        chart = size_chart or STANDARD_SIZE_CHART
        best_size = None
        best_penalty = float("inf")
        size_evaluations = {}

        for size_label, specs in chart.items():
            eval_res = self.evaluate_garment_fit(body_measurements, specs, fabric_stretch)
            size_evaluations[size_label] = eval_res

            # Asymmetric penalty: Small is penalized 4x more heavily than slightly Large
            penalty = 0.0
            for dim, info in eval_res["ease_breakdown"].items():
                ease = info["effective_ease_cm"]
                if ease < 0:
                    penalty += abs(ease) * 4.0
                elif ease > 6.0:
                    penalty += (ease - 6.0) * 1.0
                else:
                    penalty += 0.0  # Perfect fit zone

            if penalty < best_penalty:
                best_penalty = penalty
                best_size = size_label

        return {
            "recommended_size": best_size,
            "evaluation": size_evaluations[best_size],
            "all_sizes": size_evaluations
        }
