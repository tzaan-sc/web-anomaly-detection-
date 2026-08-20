"""Train and tune Isolation Forest for StudyDrive window-level features - VERSION 2 (v2).

Usage:
    python -m ml.train_v2 --features-dir data/processed/features_v2 --output-dir artifacts/models/iforest_v2 --tune
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from ml.build_features import FEATURE_COLUMNS, validate_feature_matrix
from ml.train import load_feature_list, load_split, prepare_x, anomaly_score, predict_from_threshold, metrics_for, train_one

MODEL_VERSION_V2 = "iforest_v2"
DATASET_VERSION_V2 = "features_v2"
DEFAULT_PERCENTILE = 95.0
RANDOM_STATE = 20260706


def tune_model_v2(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    feature_list: list[str],
) -> tuple[IsolationForest, dict[str, Any], pd.DataFrame]:
    candidates: list[dict[str, Any]] = []
    best_model: IsolationForest | None = None
    best_result: dict[str, Any] | None = None
    best_key: tuple[float, float, float] | None = None

    for n_estimators in [100, 200, 300]:
        for max_samples in ["auto", 128, 256]:
            for percentile in [88.0, 90.0, 92.5, 95.0, 97.0]:
                model, threshold, result = train_one(
                    train_df,
                    validation_df,
                    feature_list,
                    n_estimators=n_estimators,
                    max_samples=max_samples,
                    percentile=percentile,
                )
                val = result["validation_metrics"]
                key = (
                    float(val["f1"]),
                    -float(val["false_positive_rate"]),
                    float(val["recall"]),
                )
                row = {
                    "n_estimators": n_estimators,
                    "max_samples": str(max_samples),
                    "threshold_percentile": percentile,
                    "threshold": threshold,
                    "precision": val["precision"],
                    "recall": val["recall"],
                    "f1": val["f1"],
                    "false_positive_rate": val["false_positive_rate"],
                    "accuracy": val["accuracy"],
                    "train_flagged_ratio": result["train_flagged_ratio"],
                }
                candidates.append(row)
                if best_key is None or key > best_key:
                    best_key = key
                    best_model = model
                    best_result = result

    if best_model is None or best_result is None:
        raise RuntimeError("Không train được candidate nào.")
    return best_model, best_result, pd.DataFrame(candidates).sort_values(
        ["f1", "false_positive_rate", "recall"], ascending=[False, True, False]
    )


def save_artifact_v2(
    model: IsolationForest,
    output_dir: str | Path,
    feature_list: list[str],
    result: dict[str, Any],
    *,
    features_dir: str | Path,
) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    threshold = float(result["threshold"])
    metadata = {
        "model_version": MODEL_VERSION_V2,
        "dataset_version": DATASET_VERSION_V2,
        "features_dir": str(features_dir),
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_state": RANDOM_STATE,
        "feature_list": feature_list,
        "threshold": threshold,
        "threshold_percentile": result["threshold_percentile"],
        "parameters": {
            "n_estimators": result["n_estimators"],
            "max_samples": result["max_samples"],
            "contamination": "auto",
        },
        "train_metrics": result.get("train_metrics", {}),
        "validation_metrics": result.get("validation_metrics", {}),
    }
    artifact = {"model": model, "feature_list": feature_list, "threshold": threshold, "metadata": metadata}
    model_path = out / "model.joblib"
    joblib.dump(artifact, model_path)
    (out / "model_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "feature_list.json").write_text(json.dumps(feature_list, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "baseline_metrics.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return model_path


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Train/tune Isolation Forest cho StudyDrive features v2.")
    parser.add_argument("--features-dir", default="data/processed/features_v2")
    parser.add_argument("--output-dir", default="artifacts/models/iforest_v2")
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-samples", default="auto")
    parser.add_argument("--threshold-percentile", type=float, default=DEFAULT_PERCENTILE)
    parser.add_argument("--tune", action="store_true", help="Chạy grid tuning trên validation")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    feature_list = load_feature_list(args.features_dir)
    train_df = load_split(args.features_dir, "train")
    validation_df = load_split(args.features_dir, "validation")

    max_samples: str | int = args.max_samples
    if isinstance(max_samples, str) and max_samples.isdigit():
        max_samples = int(max_samples)

    if args.tune:
        model, result, tuning_df = tune_model_v2(train_df, validation_df, feature_list)
        Path("artifacts/metrics").mkdir(parents=True, exist_ok=True)
        tuning_df.to_csv("artifacts/metrics/tuning_results_v2.csv", index=False, encoding="utf-8-sig")
    else:
        model, threshold, result = train_one(
            train_df,
            validation_df,
            feature_list,
            n_estimators=args.n_estimators,
            max_samples=max_samples,
            percentile=args.threshold_percentile,
        )

    model_path = save_artifact_v2(model, args.output_dir, feature_list, result, features_dir=args.features_dir)
    print("=== [VERSION 2] Train Completed Successfully ===")
    print(f"  Model saved to: {model_path}")
    print(f"  Optimal Threshold: {result['threshold']:.6f}")
    print(f"  Train Set Rows: {result['train_metrics']['rows']}")
    print(f"  Validation Set Rows: {result['validation_metrics']['rows']}")
    print(f"  Validation F1-Score: {result['validation_metrics']['f1']:.4f}")
    print(f"  Validation Precision: {result['validation_metrics']['precision']:.4f}")
    print(f"  Validation Recall: {result['validation_metrics']['recall']:.4f}")


if __name__ == "__main__":
    main()
