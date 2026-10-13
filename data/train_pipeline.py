"""
Model 1 Training & Evaluation Pipeline.
Extracts geometric features from BodyM train set, trains multi-output regularized regressor,
evaluates on testB, and exports production artifacts.
"""
import os
import sys
import time
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# Add workspace to path
sys.path.insert(0, os.path.abspath("."))
from models.measurement.feature_extractor import SilhouetteFeatureExtractor


TARGETS = ["chest", "waist", "hip"]
CACHE_TRAIN = "data/cache_train_features.pkl"
CACHE_TESTB = "data/cache_testb_features.pkl"
ARTIFACTS_DIR = "models/measurement/artifacts"


def extract_split_features(
    split_dir: str,
    cache_path: str,
    max_subjects: int = None
) -> Tuple[np.ndarray, np.ndarray, List[str], pd.DataFrame]:
    """
    Extracts geometric features from BodyM split directory.
    Uses caching for fast subsequent iterations.
    """
    if os.path.exists(cache_path):
        print(f"Loading cached features from {cache_path}...")
        with open(cache_path, "rb") as f:
            data = pickle.load(f)
        return data["X"], data["Y"], data["feature_names"], data["df_meta"]

    print(f"Extracting features from {split_dir}...")
    hwg_path = os.path.join(split_dir, "hwg_metadata.csv")
    meas_path = os.path.join(split_dir, "measurements.csv")
    pmap_path = os.path.join(split_dir, "subject_to_photo_map.csv")
    mask_dir = os.path.join(split_dir, "mask")
    left_dir = os.path.join(split_dir, "mask_left")

    df_hwg = pd.read_csv(hwg_path)
    df_meas = pd.read_csv(meas_path)
    df_pmap = pd.read_csv(pmap_path)

    # Deduplicate photo map by taking first valid photo pair per subject
    df_pmap_unique = df_pmap.drop_duplicates(subset=["subject_id"], keep="first")

    merged = pd.merge(df_hwg, df_meas, on="subject_id")
    merged = pd.merge(merged, df_pmap_unique, on="subject_id")

    if max_subjects:
        merged = merged.head(max_subjects)

    extractor = SilhouetteFeatureExtractor()
    feature_rows = []
    target_rows = []
    valid_indices = []

    total = len(merged)
    t0 = time.time()

    for idx, row in merged.iterrows():
        photo_id = row["photo_id"]
        front_path = os.path.join(mask_dir, f"{photo_id}.png")
        side_path = os.path.join(left_dir, f"{photo_id}.png")

        if not (os.path.exists(front_path) and os.path.exists(side_path)):
            continue

        front_mask = cv2_imread_grayscale(front_path)
        side_mask = cv2_imread_grayscale(side_path)

        try:
            feats = extractor.extract_features(
                front_mask=front_mask,
                side_mask=side_mask,
                height_cm=float(row["height_cm"]),
                weight_kg=float(row["weight_kg"]),
                gender=str(row["gender"])
            )
            feature_rows.append(feats)
            target_rows.append([float(row[t]) for t in TARGETS])
            valid_indices.append(idx)
        except Exception:
            continue

        if len(feature_rows) % 250 == 0:
            elapsed = time.time() - t0
            print(f"Processed {len(feature_rows)}/{total} samples ({elapsed:.1f}s)...")

    feature_names = list(feature_rows[0].keys())
    X = np.array([[row[k] for k in feature_names] for row in feature_rows], dtype=np.float32)
    Y = np.array(target_rows, dtype=np.float32)
    df_valid = merged.iloc[valid_indices].reset_index(drop=True)

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "wb") as f:
        pickle.dump({"X": X, "Y": Y, "feature_names": feature_names, "df_meta": df_valid}, f)

    print(f"Saved {len(X)} samples to {cache_path} in {time.time()-t0:.1f}s.")
    return X, Y, feature_names, df_valid


def cv2_imread_grayscale(path: str) -> np.ndarray:
    import cv2
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


def train_and_evaluate():
    print("=" * 60)
    print("Starting Model 1 Multi-Target Training Pipeline")
    print("=" * 60)

    # 1. Ingest train split
    X_train, Y_train, feature_names, _ = extract_split_features(
        split_dir="train/train",
        cache_path=CACHE_TRAIN
    )
    print(f"Training Matrix X: {X_train.shape}, Targets Y: {Y_train.shape}")

    # 2. Ingest testB split
    X_test, Y_test, _, _ = extract_split_features(
        split_dir="testB/testB",
        cache_path=CACHE_TESTB
    )
    print(f"TestB Matrix X: {X_test.shape}, Targets Y: {Y_test.shape}")

    # 3. Model Training & Validation
    models = {
        "Ridge_alpha_1.0": Ridge(alpha=1.0),
        "Ridge_alpha_10.0": Ridge(alpha=10.0),
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    }

    best_model_name = None
    best_overall_mae = float("inf")
    best_pipeline = None
    all_metrics = {}

    for name, reg in models.items():
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", reg)
        ])
        pipe.fit(X_train, Y_train)
        Y_pred = pipe.predict(X_test)

        mae_per_target = {}
        r2_per_target = {}
        for i, target in enumerate(TARGETS):
            mae = mean_absolute_error(Y_test[:, i], Y_pred[:, i])
            r2 = r2_score(Y_test[:, i], Y_pred[:, i])
            mae_per_target[target] = float(mae)
            r2_per_target[target] = float(r2)

        mean_mae = float(np.mean(list(mae_per_target.values())))
        all_metrics[name] = {
            "mean_mae": mean_mae,
            "mae_per_target": mae_per_target,
            "r2_per_target": r2_per_target
        }
        print(f"\n--- {name} Results on TestB ---")
        print(f"Mean MAE across targets: {mean_mae:.3f} cm")
        for t in TARGETS:
            print(f"  {t.capitalize()}: MAE = {mae_per_target[t]:.3f} cm | R2 = {r2_per_target[t]:.3f}")

        if mean_mae < best_overall_mae:
            best_overall_mae = mean_mae
            best_model_name = name
            best_pipeline = pipe

    print(f"\nOptimal Model Selected: {best_model_name} (Mean MAE: {best_overall_mae:.3f} cm)")

    # 4. Export Artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    model_artifact_path = os.path.join(ARTIFACTS_DIR, "regressor_model.pkl")
    with open(model_artifact_path, "wb") as f:
        pickle.dump(best_pipeline, f)

    meta = {
        "best_model": best_model_name,
        "targets": TARGETS,
        "feature_names": feature_names,
        "testb_metrics": all_metrics[best_model_name],
        "training_samples": len(X_train),
        "testb_samples": len(X_test),
        "all_benchmarks": all_metrics
    }
    meta_path = os.path.join(ARTIFACTS_DIR, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nArtifacts successfully exported:")
    print(f"  - Model: {model_artifact_path}")
    print(f"  - Metadata: {meta_path}")
    return meta


if __name__ == "__main__":
    train_and_evaluate()
