"""
Router for Model 2: Garment Fit & Kinematic Ease Sizing Recommendation.
"""
from fastapi import APIRouter, Depends
from app.schemas.fit import FitEvaluationRequest, SizeRecommendationRequest, FitResponse
from app.dependencies import get_fit_engine
from models.fit.fit_engine import FitEngine

router = APIRouter(prefix="/api/v1", tags=["Model 2: Sizing & Fit"])


@router.post("/recommend", response_model=FitResponse)
def evaluate_fit(
    request: FitEvaluationRequest,
    fit_engine: FitEngine = Depends(get_fit_engine)
):
    """
    Evaluates fit classification (Small, Fit, Large) for a specific garment dimension set.
    """
    if request.garment_specs:
        result = fit_engine.evaluate_garment_fit(
            body_measurements=request.body_measurements,
            garment_specs=request.garment_specs,
            fabric_stretch=request.fabric_stretch
        )
        return FitResponse(
            status="success",
            fit_category=result["fit_category"],
            primary_ease_cm=result["primary_ease_cm"],
            verdict=result["verdict"],
            ease_breakdown=result["ease_breakdown"]
        )
    else:
        # If no garment specs provided, find best standard size
        rec = fit_engine.recommend_best_size(
            body_measurements=request.body_measurements,
            fabric_stretch=request.fabric_stretch
        )
        eval_res = rec["evaluation"]
        return FitResponse(
            status="success",
            recommended_size=rec["recommended_size"],
            fit_category=eval_res["fit_category"],
            primary_ease_cm=eval_res["primary_ease_cm"],
            verdict=f"Recommended size: {rec['recommended_size']}. {eval_res['verdict']}",
            ease_breakdown=eval_res["ease_breakdown"]
        )


@router.post("/recommend/best-size")
def recommend_optimal_size(
    request: SizeRecommendationRequest,
    fit_engine: FitEngine = Depends(get_fit_engine)
):
    """
    Determines the optimal size from a brand size chart minimizing return probability.
    """
    rec = fit_engine.recommend_best_size(
        body_measurements=request.body_measurements,
        size_chart=request.size_chart,
        fabric_stretch=request.fabric_stretch
    )
    return {
        "status": "success",
        "recommended_size": rec["recommended_size"],
        "evaluation": rec["evaluation"],
        "all_sizes": rec["all_sizes"]
    }
