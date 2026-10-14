"""
Model 2: Garment Fit & Kinematic Ease Recommendation Engine.
Analyzes anthropometric ease allowances, textile stretch factors, garment profiles,
and brand size charts to provide deterministic fit classifications (Small, Fit, Large),
optimal size selection, and return-probability risk modeling.
"""
import math
from typing import Dict, Any, Optional, List, Tuple
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
    Computes garment-to-body kinematic ease allowances, retail return-risk probabilities,
    and determines ergonomic fit classifications across diverse garment types.
    """

    GARMENT_PROFILES = {
        "regular": {
            "chest": {"tight_bound": 0.0, "loose_bound": 10.0, "weight": 0.50},
            "waist": {"tight_bound": 0.5, "loose_bound": 8.0, "weight": 0.30},
            "hip": {"tight_bound": 1.5, "loose_bound": 10.0, "weight": 0.20},
            "description": "Standard everyday apparel with balanced drape and mobility."
        },
        "shirt": {
            "chest": {"tight_bound": 2.0, "loose_bound": 8.0, "weight": 0.55},
            "waist": {"tight_bound": 1.0, "loose_bound": 7.0, "weight": 0.30},
            "hip": {"tight_bound": 1.0, "loose_bound": 8.0, "weight": 0.15},
            "description": "Tailored woven dress shirts and casual button-downs."
        },
        "t_shirt": {
            "chest": {"tight_bound": 0.0, "loose_bound": 7.0, "weight": 0.60},
            "waist": {"tight_bound": 0.0, "loose_bound": 6.0, "weight": 0.25},
            "hip": {"tight_bound": 0.5, "loose_bound": 7.0, "weight": 0.15},
            "description": "Jersey knit t-shirts with flexible ergonomic drape."
        },
        "jacket": {
            "chest": {"tight_bound": 6.0, "loose_bound": 16.0, "weight": 0.50},
            "waist": {"tight_bound": 4.0, "loose_bound": 14.0, "weight": 0.30},
            "hip": {"tight_bound": 4.0, "loose_bound": 14.0, "weight": 0.20},
            "description": "Outerwear coats and blazers designed for layering over clothing."
        },
        "activewear": {
            "chest": {"tight_bound": -4.0, "loose_bound": 3.0, "weight": 0.50},
            "waist": {"tight_bound": -3.0, "loose_bound": 3.0, "weight": 0.30},
            "hip": {"tight_bound": -3.0, "loose_bound": 4.0, "weight": 0.20},
            "description": "Athletic and compression garments designed for second-skin elastic tension."
        },
        "pants": {
            "waist": {"tight_bound": 0.5, "loose_bound": 4.0, "weight": 0.60},
            "hip": {"tight_bound": 1.5, "loose_bound": 6.0, "weight": 0.40},
            "description": "Trousers, jeans, and shorts governed by waist and hip circumference."
        }
    }

    # Backward-compatible reference
    DEFAULT_TOLERANCES = GARMENT_PROFILES["regular"]

    @classmethod
    def get_garment_tolerances(cls, garment_type: Optional[str]) -> Dict[str, Dict[str, float]]:
        """Retrieves calibrated tolerance bounds by garment classification."""
        clean_type = str(garment_type or "regular").strip().lower()
        return cls.GARMENT_PROFILES.get(clean_type, cls.GARMENT_PROFILES["regular"])

    @staticmethod
    def normalize_measurement_keys(measurements: Dict[str, float]) -> Dict[str, float]:
        """Normalizes dimension keys (e.g. 'chest_cm' -> 'chest')."""
        alias_map = {
            "chest_cm": "chest", "bust_cm": "chest", "chest": "chest", "bust": "chest",
            "waist_cm": "waist", "waist": "waist",
            "hip_cm": "hip", "hips_cm": "hip", "hip": "hip", "hips": "hip",
            "shoulder_cm": "shoulder", "shoulder": "shoulder",
            "thigh_cm": "thigh", "thigh": "thigh",
            "calf_cm": "calf", "calf": "calf"
        }
        normalized = {}
        for k, v in measurements.items():
            clean_k = str(k).strip().lower()
            canonical_k = alias_map.get(clean_k, clean_k)
            try:
                normalized[canonical_k] = float(v)
            except (ValueError, TypeError):
                continue
        return normalized

    @classmethod
    def compute_dimension_completeness(
        cls,
        norm_body: Dict[str, float],
        norm_garment: Dict[str, float],
        size_label: Optional[str] = None
    ) -> Tuple[List[str], List[str], List[str], List[str], float, Optional[str]]:
        """
        Evaluates presence of standard anthropometric girths (chest, waist, hip)
        across BOTH human body measurements and garment specifications.

        Returns:
            evaluated_dims: Standard dimensions present in both body and garment specs
            missing_body_dims: Standard dimensions missing from human body measurements
            missing_garment_dims: Standard dimensions missing from garment specifications
            missing_dims: Union of all standard dimensions missing from either body or garment
            confidence: Calibrated reliability confidence score [0.0 to 1.0]
            warning: Explicit transparent warning explaining omissions and implications
        """
        all_standard = ["chest", "waist", "hip"]
        evaluated_dims = [dim for dim in all_standard if dim in norm_body and dim in norm_garment]
        missing_body_dims = [dim for dim in all_standard if dim not in norm_body]
        missing_garment_dims = [dim for dim in all_standard if dim not in norm_garment]
        missing_dims = [dim for dim in all_standard if dim not in norm_body or dim not in norm_garment]

        num_evaluated = len(evaluated_dims)
        has_chest = "chest" in evaluated_dims
        has_waist = "waist" in evaluated_dims
        has_hip = "hip" in evaluated_dims

        if num_evaluated == 3:
            confidence = 1.0
        elif has_chest and has_waist:
            confidence = 0.85
        elif has_chest and has_hip:
            confidence = 0.80
        elif has_waist and has_hip:
            confidence = 0.80
        elif has_chest:
            confidence = 0.70
        else:
            confidence = 0.60

        warning_parts = []
        size_str = f"Garment size '{size_label}'" if size_label else "Garment specification"

        if missing_garment_dims and missing_body_dims:
            warning_parts.append(
                f"Partial evaluation: Missing body measurement(s) {missing_body_dims} "
                f"and {size_str} is missing dimension(s) {missing_garment_dims}. "
                f"Fit evaluated solely on common dimension(s) ({', '.join(evaluated_dims)})."
            )
        elif missing_garment_dims:
            warning_parts.append(
                f"Partial evaluation: {size_str} is missing measurement(s) {missing_garment_dims}. "
                f"Ease evaluated only for available dimensions ({', '.join(evaluated_dims)}). "
                f"For full multi-point confidence, provide garment {', '.join(missing_garment_dims)} measurement."
            )
        elif missing_body_dims:
            if missing_body_dims == ["hip"]:
                warning_parts.append(
                    f"Partial evaluation: Missing body measurement(s) ['hip']. "
                    f"Sizing recommendation is computed from available girths ({', '.join(evaluated_dims)}). "
                    f"For full multi-point confidence, provide hip measurement."
                )
            elif missing_body_dims == ["waist"]:
                warning_parts.append(
                    f"Partial evaluation: Missing body measurement(s) ['waist']. "
                    f"Sizing recommendation is computed from chest and hip."
                )
            elif missing_body_dims == ["chest"]:
                warning_parts.append(
                    "Partial evaluation: Missing 'chest' measurement. Suitable primarily for lower-body garments."
                )
            else:
                warning_parts.append(
                    f"Partial evaluation: Sizing is based solely on {list(norm_body.keys())}."
                )

        warning = " ".join(warning_parts) if warning_parts else None

        return evaluated_dims, missing_body_dims, missing_garment_dims, missing_dims, confidence, warning

    @classmethod
    def detect_dimension_conflict(
        cls,
        norm_body: Dict[str, float],
        chart: Optional[Dict[str, Dict[str, float]]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Detects athletic or divergent body shapes where different body girths
        map to sizes separated by 2 or more standard sizes (e.g. XL chest with S waist).
        """
        size_chart = chart or STANDARD_SIZE_CHART
        size_order = list(size_chart.keys())

        implied_sizes = {}
        for dim in ["chest", "waist"]:
            if dim in norm_body:
                val = norm_body[dim]
                best_idx = None
                best_diff = float("inf")
                for idx, (label, specs) in enumerate(size_chart.items()):
                    if dim in specs:
                        diff = abs(specs[dim] - val)
                        if diff < best_diff:
                            best_diff = diff
                            best_idx = idx
                if best_idx is not None:
                    implied_sizes[dim] = best_idx

        if "chest" in implied_sizes and "waist" in implied_sizes:
            diff = abs(implied_sizes["chest"] - implied_sizes["waist"])
            if diff >= 2:
                c_label = size_order[implied_sizes["chest"]]
                w_label = size_order[implied_sizes["waist"]]
                note = (
                    f"Dimension divergence detected: Chest maps to Size {c_label} while Waist maps to Size {w_label}. "
                    "Sizing recommendation is prioritized for thoracic comfort; a tailored athletic taper is recommended."
                )
                return True, note

        return False, None

    @staticmethod
    def compute_return_risk(
        category: str,
        penalty: float,
        stretch_ratio: float = 0.0,
        is_close_fit: bool = False
    ) -> float:
        """
        Calibrated return-risk probability based on asymmetric loss, fit category,
        and dynamic textile elastane stretch mitigation.
        Empirical retail data: tightness causes 68% of returns, excessive looseness causes 22%.
        Dynamic fabric elasticity relieves constriction and significantly lowers return risk for close/tailored fits.
        """
        stretch_benefit = min(0.04, stretch_ratio * 0.12) if is_close_fit else 0.0

        if category == FitCategory.FIT.value:
            # Baseline return risk for well-fitting garments (3% to 8%), mitigated by stretch
            base = 0.04 + (penalty * 0.02)
            return round(max(0.02, min(0.10, base - stretch_benefit)), 3)
        elif category == FitCategory.SMALL.value:
            # High return risk for tight clothing, slightly mitigated by stretch
            base = 0.25 + (penalty * 0.06)
            return round(max(0.20, min(0.95, base - (stretch_ratio * 0.08))), 3)
        else:
            # Moderate return risk for loose clothing
            return round(min(0.80, 0.15 + (penalty * 0.03)), 3)

    @classmethod
    def identify_garment_size_label(cls, garment_specs: Dict[str, float]) -> Optional[str]:
        """
        Identifies which standard size (XS, S, M, L, XL, XXL) a garment specification
        most closely corresponds to on the standard size chart using weighted anatomical distance.
        """
        norm_specs = cls.normalize_measurement_keys(garment_specs)
        best_label = None
        best_diff = float("inf")

        for label, chart_specs in STANDARD_SIZE_CHART.items():
            diff = 0.0
            count = 0.0
            for dim, chart_val in chart_specs.items():
                if dim in norm_specs:
                    w = cls.DEFAULT_TOLERANCES.get(dim, {}).get("weight", 0.33)
                    diff += (abs(norm_specs[dim] - chart_val) ** 2) * w
                    count += w
            if count > 0:
                weighted_rmse = (diff / count) ** 0.5
                if weighted_rmse < best_diff:
                    best_diff = weighted_rmse
                    best_label = label

        return best_label

    @staticmethod
    def compute_size_advice(
        evaluated_size: Optional[str],
        recommended_size: Optional[str],
        fit_category: str
    ) -> Optional[str]:
        """
        Generates clear directional sizing advice comparing the tested garment's size
        with the user's recommended optimal size.
        """
        if not evaluated_size or not recommended_size:
            return None

        size_order = ["XS", "S", "M", "L", "XL", "XXL"]
        if evaluated_size in size_order and recommended_size in size_order:
            eval_idx = size_order.index(evaluated_size)
            rec_idx = size_order.index(recommended_size)
            diff = rec_idx - eval_idx

            if diff > 0:
                step_str = f"{diff} size" if diff == 1 else f"{diff} sizes"
                return f"Size up to {recommended_size} (tested garment {evaluated_size} is {step_str} smaller than your ideal fit)"
            elif diff < 0:
                step_str = f"{abs(diff)} size" if abs(diff) == 1 else f"{abs(diff)} sizes"
                return f"Size down to {recommended_size} (tested garment {evaluated_size} is {step_str} larger than your ideal fit)"
            else:
                return f"True to size ({recommended_size})"

        if fit_category == FitCategory.SMALL.value:
            return f"Recommend sizing up to {recommended_size}"
        elif fit_category == FitCategory.LARGE.value:
            return f"Recommend sizing down to {recommended_size}"
        return f"True to size ({recommended_size})"

    def evaluate_garment_fit(
        self,
        body_measurements: Dict[str, float],
        garment_specs: Dict[str, float],
        fabric_stretch: float = 0.0,
        garment_type: Optional[str] = "regular",
        evaluated_size: Optional[str] = None,
        recommended_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates fit category for a specific garment specification against body measurements.
        """
        norm_body = self.normalize_measurement_keys(body_measurements)
        norm_garment = self.normalize_measurement_keys(garment_specs)

        # Defensive runtime guard against non-finite floating point values (NaN, Inf)
        for dim, val in list(norm_body.items()):
            if not isinstance(val, (int, float)) or not math.isfinite(val) or math.isnan(val):
                raise ValueError(f"Body measurement for '{dim}' must be a finite numeric value, received {val!r}.")
        for dim, val in list(norm_garment.items()):
            if not isinstance(val, (int, float)) or not math.isfinite(val) or math.isnan(val):
                raise ValueError(f"Garment dimension for '{dim}' must be a finite numeric value, received {val!r}.")

        tolerances = self.get_garment_tolerances(garment_type)

        evaluated_dims, missing_body_dims, missing_garment_dims, missing_dims, confidence, warning = (
            self.compute_dimension_completeness(norm_body, norm_garment, size_label=evaluated_size)
        )

        ease_breakdown = {}
        category_votes = []

        primary_dim = "chest" if "chest" in norm_body and "chest" in norm_garment else None
        if not primary_dim:
            if evaluated_dims:
                primary_dim = evaluated_dims[0]
            else:
                primary_dim = "chest"

        if isinstance(fabric_stretch, str):
            stretch_map = {"none": 0.0, "low": 0.05, "medium": 0.12, "high": 0.25, "elastic": 0.35}
            stretch_val = stretch_map.get(fabric_stretch.strip().lower(), 0.0)
        else:
            try:
                stretch_val = float(fabric_stretch)
            except (ValueError, TypeError):
                stretch_val = 0.0
        stretch_ratio = max(0.0, min(stretch_val, 0.60))

        total_penalty = 0.0

        for dim, body_val in norm_body.items():
            if dim in norm_garment:
                garment_val = float(norm_garment[dim])
                static_ease = garment_val - float(body_val)
                comfort_stretch_ratio = min(stretch_ratio, 0.20)
                comfort_reserve = garment_val * comfort_stretch_ratio
                theoretical_capacity = garment_val * stretch_ratio

                tol = tolerances.get(dim, {"tight_bound": 0.0, "loose_bound": 10.0, "weight": 0.20})
                base_tight = tol["tight_bound"]
                loose_bound = tol["loose_bound"]
                weight = tol.get("weight", 0.20)

                # Woven (stretch < 0.05) cannot tolerate negative ease (< 0.0 cm).
                # Stretch fabrics allow light contouring, capped strictly at -1.5 cm.
                max_neg_tol = -1.5 if stretch_ratio >= 0.05 else 0.0
                effective_tight_bound = max(max_neg_tol, base_tight - (comfort_reserve * 0.10))

                if static_ease < effective_tight_bound:
                    cat = FitCategory.SMALL
                    deficit = abs(static_ease - effective_tight_bound)
                    total_penalty += (deficit * 4.0 + 2.0) * weight
                elif static_ease <= loose_bound:
                    cat = FitCategory.FIT
                    # High stretch mitigates discomfort penalty for close fits
                    stretch_discount = max(0.60, 1.0 - (stretch_ratio * 0.8))
                    total_penalty += abs(static_ease - (base_tight + 3.0)) * 0.1 * weight * stretch_discount
                else:
                    cat = FitCategory.LARGE
                    excess = static_ease - loose_bound
                    total_penalty += (excess * 1.5 + 1.0) * weight

                ease_breakdown[dim] = {
                    "body_cm": round(float(body_val), 1),
                    "garment_cm": round(float(garment_val), 1),
                    "effective_ease_cm": round(float(static_ease), 1),
                    "stretch_reserve_cm": round(float(comfort_reserve), 1),
                    "comfort_stretch_allowance_cm": round(float(comfort_reserve), 1),
                    "max_stretch_capacity_cm": round(float(theoretical_capacity), 1),
                    "category": cat.value
                }
                category_votes.append(cat)

        # Primary verdict determined by chest ease if available, otherwise priority vote
        if primary_dim and primary_dim in ease_breakdown:
            overall_cat = ease_breakdown[primary_dim]["category"]
            primary_ease = ease_breakdown[primary_dim]["effective_ease_cm"]
        elif category_votes:
            primary_dim = list(ease_breakdown.keys())[0]
            primary_ease = ease_breakdown[primary_dim]["effective_ease_cm"]
            if FitCategory.SMALL in category_votes:
                overall_cat = FitCategory.SMALL.value
            elif FitCategory.LARGE in category_votes and FitCategory.FIT not in category_votes:
                overall_cat = FitCategory.LARGE.value
            else:
                overall_cat = FitCategory.FIT.value
        else:
            primary_dim = "chest"
            primary_ease = 0.0
            overall_cat = FitCategory.FIT.value

        # Calculate anthropometrically weighted ease score
        total_weight = 0.0
        weighted_ease_sum = 0.0
        for dim, info in ease_breakdown.items():
            w = tolerances.get(dim, {}).get("weight", 0.20)
            weighted_ease_sum += info["effective_ease_cm"] * w
            total_weight += w

        weighted_average_ease = round(weighted_ease_sum / total_weight, 1) if total_weight > 0 else primary_ease

        is_close_fit = (primary_ease <= 4.0)
        return_risk = self.compute_return_risk(overall_cat, total_penalty, stretch_ratio=stretch_ratio, is_close_fit=is_close_fit)

        # Context-rich tailoring verdicts aligned with directional sizing advice
        size_prefix = f"Tested garment ({evaluated_size})" if evaluated_size else "Garment"
        rec_suffix = f" Recommend sizing up to {recommended_size} for comfort." if recommended_size and recommended_size != evaluated_size else " Recommend sizing up for comfort."
        rec_down_suffix = f" Recommend sizing down to {recommended_size} if tailored look is desired." if recommended_size and recommended_size != evaluated_size else " Recommend sizing down if tailored look is desired."

        if overall_cat == FitCategory.FIT.value:
            # If tested size differs from recommended size, explain the tailored fit relative to recommendation
            if evaluated_size and recommended_size and evaluated_size != recommended_size:
                if primary_ease <= 4.0:
                    verdict = (
                        f"{size_prefix} provides a close tailored fit (ease: {primary_ease:+.1f} cm, primary: {primary_dim}). "
                        f"While wearable with dynamic stretch, Size {recommended_size} is recommended for standard comfort."
                    )
                elif primary_ease <= 8.0:
                    verdict = (
                        f"{size_prefix} provides regular drape (ease: {primary_ease:+.1f} cm, primary: {primary_dim}). "
                        f"Recommended standard size is {recommended_size}."
                    )
                else:
                    verdict = (
                        f"{size_prefix} fits relaxed / roomy (ease: {primary_ease:+.1f} cm, primary: {primary_dim}). "
                        f"Recommended standard size is {recommended_size}."
                    )
            else:
                true_to_size_suffix = f"True to size ({evaluated_size})." if evaluated_size else "True to size."
                if primary_ease <= 4.0:
                    verdict = f"{size_prefix} fits tailored / slim (ease: {primary_ease:+.1f} cm, primary: {primary_dim}). {true_to_size_suffix} Dynamic stretch provides ergonomic mobility."
                elif primary_ease <= 8.0:
                    verdict = f"{size_prefix} offers optimal ergonomic drape (ease: {primary_ease:+.1f} cm, primary: {primary_dim}). Regular / classic fit."
                else:
                    verdict = f"{size_prefix} fits relaxed / comfort (ease: {primary_ease:+.1f} cm, primary: {primary_dim}). {true_to_size_suffix}"
        elif overall_cat == FitCategory.SMALL.value:
            verdict = f"{size_prefix} is too snug (ease: {primary_ease:+.1f} cm, primary: {primary_dim}).{rec_suffix}"
        else:
            verdict = f"{size_prefix} fits loose / relaxed (ease: {primary_ease:+.1f} cm, primary: {primary_dim}).{rec_down_suffix}"

        return {
            "fit_category": overall_cat,
            "primary_dimension": primary_dim,
            "primary_ease_cm": primary_ease,
            "weighted_average_ease_cm": weighted_average_ease,
            "confidence_score": confidence,
            "return_risk_score": return_risk,
            "is_partial_evaluation": len(missing_dims) > 0,
            "missing_dimensions": missing_dims,
            "missing_body_dimensions": missing_body_dims,
            "missing_garment_dimensions": missing_garment_dims,
            "evaluated_dimensions": evaluated_dims,
            "warning": warning,
            "verdict": verdict,
            "ease_breakdown": ease_breakdown
        }

    def recommend_best_size(
        self,
        body_measurements: Dict[str, float],
        size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        fabric_stretch: float = 0.0,
        garment_type: Optional[str] = "regular"
    ) -> Dict[str, Any]:
        """
        Evaluates a full brand size chart to determine the optimal size minimizing return risk.
        Uses asymmetric loss function calibrated to human pressure tolerance, normalized
        across evaluated dimensions for equitable cross-size comparisons.
        """
        chart = size_chart or STANDARD_SIZE_CHART
        tolerances = self.get_garment_tolerances(garment_type)
        best_size = None
        best_penalty = float("inf")
        size_evaluations = {}

        has_conflict, conflict_note = self.detect_dimension_conflict(body_measurements, chart)

        # Audit size chart for incomplete dimension specifications
        chart_incomplete_sizes = []
        for size_label, specs in chart.items():
            norm_specs = self.normalize_measurement_keys(specs)
            missing_in_size = [dim for dim in ["chest", "waist", "hip"] if dim not in norm_specs]
            if missing_in_size:
                chart_incomplete_sizes.append(size_label)

        for size_label, specs in chart.items():
            eval_res = self.evaluate_garment_fit(
                body_measurements, specs, fabric_stretch, garment_type, evaluated_size=size_label
            )
            size_evaluations[size_label] = eval_res

            raw_penalty = 0.0
            sum_weight = 0.0
            for dim, info in eval_res["ease_breakdown"].items():
                ease = info["effective_ease_cm"]
                stretch_reserve = info.get("stretch_reserve_cm", 0.0)
                tol = tolerances.get(dim, {"tight_bound": 0.0, "loose_bound": 10.0, "weight": 0.20})
                weight = tol.get("weight", 0.20)
                base_tight = tol["tight_bound"]
                loose_bound = tol["loose_bound"]

                if ease < base_tight:
                    # Negative ease penalty
                    unmitigated_deficit = max(0.0, abs(ease - base_tight) - (stretch_reserve * 0.15))
                    raw_penalty += (unmitigated_deficit * 4.5 + abs(ease - base_tight) * 0.8) * weight
                elif ease > loose_bound:
                    # Excess looseness penalty
                    raw_penalty += ((ease - loose_bound) * 1.5) * weight
                else:
                    # Ideal zone
                    raw_penalty += abs(ease - (base_tight + 3.0)) * 0.1 * weight

                sum_weight += weight

            # Normalize penalty by evaluated dimension weight to ensure fair comparison
            # across sizes with different numbers of dimensions
            normalized_penalty = (raw_penalty / sum_weight) if sum_weight > 0 else raw_penalty

            if normalized_penalty < best_penalty:
                best_penalty = normalized_penalty
                best_size = size_label

        if best_size is None and size_evaluations:
            best_size = next(iter(size_evaluations.keys()))
        if best_size is None:
            raise ValueError("No viable size could be evaluated from the size chart.")

        best_eval = size_evaluations[best_size]

        warning_parts = []
        if best_eval.get("warning"):
            warning_parts.append(best_eval["warning"])
        if has_conflict and conflict_note:
            warning_parts.append(conflict_note)
        if chart_incomplete_sizes and best_size not in chart_incomplete_sizes:
            warning_parts.append(
                f"Note: Size chart contains incomplete entries for size(s) {chart_incomplete_sizes}. "
                "Sizing comparisons were normalized across evaluated dimensions."
            )

        combined_warning = " ".join(warning_parts) if warning_parts else None

        return {
            "recommended_size": best_size,
            "confidence_score": best_eval["confidence_score"],
            "return_risk_score": best_eval["return_risk_score"],
            "is_partial_evaluation": best_eval["is_partial_evaluation"],
            "missing_dimensions": best_eval["missing_dimensions"],
            "missing_body_dimensions": best_eval.get("missing_body_dimensions", []),
            "missing_garment_dimensions": best_eval.get("missing_garment_dimensions", []),
            "evaluated_dimensions": best_eval["evaluated_dimensions"],
            "has_dimension_conflict": has_conflict,
            "chart_has_incomplete_sizes": len(chart_incomplete_sizes) > 0,
            "warning": combined_warning,
            "evaluation": best_eval,
            "all_sizes": size_evaluations
        }
