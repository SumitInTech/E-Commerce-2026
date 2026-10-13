"""
Router for Model 1: Anthropometric Measurement & Body Silhouette Profiling.
"""
import os
import time
import base64
from typing import Optional
import numpy as np
import cv2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.schemas.measurement import MeasurementRequest, MeasurementResponse
from app.dependencies import get_regressor
from models.measurement.regressor import BodyMeasurementRegressor
from core.exceptions import InvalidSilhouetteException

router = APIRouter(prefix="/api/v1", tags=["Model 1: Anthropometry"])


def decode_base64_image(b64_str: str) -> np.ndarray:
    """Decodes base64 string to single channel grayscale OpenCV image."""
    try:
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        img_bytes = base64.b64decode(b64_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Decoded image is None")
        return img
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid base64 image data: {str(e)}")


def find_photo_mask(photo_id: str) -> tuple[np.ndarray, np.ndarray]:
    """Searches dataset directories for photo_id masks."""
    candidates = [
        ("train/train/mask", "train/train/mask_left"),
        ("testB/testB/mask", "testB/testB/mask_left"),
        ("testA/testA/mask", "testA/testA/mask_left"),
    ]
    for front_dir, left_dir in candidates:
        front_p = os.path.join(front_dir, f"{photo_id}.png")
        left_p = os.path.join(left_dir, f"{photo_id}.png")
        if os.path.exists(front_p) and os.path.exists(left_p):
            m1 = cv2.imread(front_p, cv2.IMREAD_GRAYSCALE)
            m2 = cv2.imread(left_p, cv2.IMREAD_GRAYSCALE)
            return m1, m2

    raise HTTPException(status_code=404, detail=f"Photo ID '{photo_id}' not found in dataset directories.")


@router.post("/fit-check", response_model=MeasurementResponse)
def compute_measurements(
    request: MeasurementRequest,
    regressor: BodyMeasurementRegressor = Depends(get_regressor)
):
    """
    Computes 3D body circumferences (chest, waist, hip) from user photos/masks and metadata.
    """
    t0 = time.time()

    front_mask = None
    side_mask = None

    if request.photo_id:
        front_mask, side_mask = find_photo_mask(request.photo_id)
    elif request.front_mask_base64 and request.side_mask_base64:
        front_mask = decode_base64_image(request.front_mask_base64)
        side_mask = decode_base64_image(request.side_mask_base64)
    else:
        # Fallback to demo sample if none provided
        sample_id = "001f3a88501980a5eca6f6346a0ca8d9"
        try:
            front_mask, side_mask = find_photo_mask(sample_id)
        except Exception:
            raise HTTPException(
                status_code=422,
                detail="Either photo_id or front_mask_base64 + side_mask_base64 must be provided."
            )

    try:
        res = regressor.predict_from_masks(
            front_mask=front_mask,
            side_mask=side_mask,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            gender=request.gender
        )
    except InvalidSilhouetteException as e:
        raise HTTPException(status_code=422, detail=f"Silhouette extraction failed: {e.message}")

    latency_ms = (time.time() - t0) * 1000.0

    return MeasurementResponse(
        status="success",
        predictions=res["predictions"],
        extracted_features=res["extracted_features"],
        model_type=res["model_type"],
        latency_ms=round(latency_ms, 2)
    )


@router.post("/fit-check/upload", response_model=MeasurementResponse)
async def upload_fit_check(
    height_cm: float = Form(...),
    weight_kg: float = Form(...),
    gender: str = Form(...),
    front_image: UploadFile = File(...),
    side_image: UploadFile = File(...),
    regressor: BodyMeasurementRegressor = Depends(get_regressor)
):
    """
    Accepts raw multipart file uploads for front and side silhouette images.
    """
    t0 = time.time()

    front_bytes = await front_image.read()
    side_bytes = await side_image.read()

    front_nparr = np.frombuffer(front_bytes, np.uint8)
    side_nparr = np.frombuffer(side_bytes, np.uint8)

    front_mask = cv2.imdecode(front_nparr, cv2.IMREAD_GRAYSCALE)
    side_mask = cv2.imdecode(side_nparr, cv2.IMREAD_GRAYSCALE)

    if front_mask is None or side_mask is None:
        raise HTTPException(status_code=422, detail="Failed to decode uploaded image files.")

    try:
        res = regressor.predict_from_masks(
            front_mask=front_mask,
            side_mask=side_mask,
            height_cm=height_cm,
            weight_kg=weight_kg,
            gender=gender
        )
    except InvalidSilhouetteException as e:
        raise HTTPException(status_code=422, detail=f"Silhouette extraction failed: {e.message}")

    latency_ms = (time.time() - t0) * 1000.0

    return MeasurementResponse(
        status="success",
        predictions=res["predictions"],
        extracted_features=res["extracted_features"],
        model_type=res["model_type"],
        latency_ms=round(latency_ms, 2)
    )
