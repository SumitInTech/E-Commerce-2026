"""
Model 1 Production Inference Wrapper.
Loads the serialized multi-output regression pipeline and metadata,
computes calibrated geometric features, and infers 3D body circumferences.
"""
import os
import json
import pickle
from typing import Dict, Any, Optional
import numpy as np

from core.exceptions import ModelArtifactNotFoundException, InvalidSilhouetteException
from core.config import settings
from models.measurement.feature_extractor import SilhouetteFeatureExtractor


class BodyMeasurementRegressor:
    """
    Inference service for Model 1: Body Measurement Regressor.
    """

    def __init__(self, model_path: Optional[str] = None, metadata_path: Optional[str] = None):
        self.model_path = model_path or settings.REGRESSOR_MODEL_PATH
        self.metadata_path = metadata_path or settings.METADATA_PATH
        self.pipeline = None
        self.metadata = None
        self.feature_names = []
        self.targets = ["chest", "waist", "hip"]
        self.extractor = SilhouetteFeatureExtractor()

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        if not os.path.exists(self.model_path):
            raise ModelArtifactNotFoundException(
                f"Model weights artifact not found at '{self.model_path}'. "
                "Ensure training pipeline has completed."
            )

        with open(self.model_path, "rb") as f:
            self.pipeline = pickle.load(f)

        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r") as f:
                self.metadata = json.load(f)
                self.feature_names = self.metadata.get("feature_names", [])
                self.targets = self.metadata.get("targets", self.targets)

    def predict_from_features(self, features_dict: Dict[str, float]) -> Dict[str, float]:
        """
        Runs inference on pre-extracted feature dictionary.
        """
        if not self.feature_names:
            self.feature_names = list(features_dict.keys())

        x_vec = np.array([[features_dict[k] for k in self.feature_names]], dtype=np.float32)
        y_pred = self.pipeline.predict(x_vec)[0]

        predictions = {}
        for idx, target in enumerate(self.targets):
            predictions[f"{target}_cm"] = round(float(y_pred[idx]), 1)

        return predictions

    def predict_from_masks(
        self,
        front_mask: np.ndarray,
        side_mask: np.ndarray,
        height_cm: float,
        weight_kg: float,
        gender: str
    ) -> Dict[str, Any]:
        """
        End-to-end inference from dual masks + demographic metadata.
        """
        features = self.extractor.extract_features(
            front_mask=front_mask,
            side_mask=side_mask,
            height_cm=height_cm,
            weight_kg=weight_kg,
            gender=gender
        )

        predictions = self.predict_from_features(features)

        return {
            "predictions": predictions,
            "extracted_features": features,
            "model_type": self.metadata.get("best_model", "RandomForest") if self.metadata else "Trained"
        }
