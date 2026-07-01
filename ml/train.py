"""Train and tune Isolation Forest for StudyDrive window-level features.

Baseline:
    python -m ml.train --features-dir data/processed/features_v1

Grid tuning on validation:
    python -m ml.train --features-dir data/processed/features_v1 --tune
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

from ml.build_features import FEATURE_COLUMNS, DATASET_VERSION, validate_feature_matrix

MODEL_VERSION = "iforest_v1"
DEFAULT_PERCENTILE = 95.0
RANDOM_STATE = 20260706


def load_feature_list(features_dir: str | Path) -> list[str]:
    path = Path(features_dir) / "feature_list.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return list(FEATURE_COLUMNS)


def load_split(features_dir: str | Path, split_name: str) -> pd.DataFrame:
    path = Path(features_dir) / f"{split_name}_features.csv"
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy {path}. Chạy `python -m ml.build_features` trước.")
    return pd.read_csv(path, encoding="utf-8-sig")


def prepare_x(df: pd.DataFrame, feature_list: list[str]) -> pd.DataFrame:
    validate_feature_matrix(df, feature_list)
    return df[feature_list].apply(pd.to_numeric, errors="coerce").fillna(0.0)


def anomaly_score(model: IsolationForest, x: pd.DataFrame) -> np.ndarray:
    """Return score where larger value means more anomalous."""
    return -model.score_samples(x)


def predict_from_threshold(scores: np.ndarray, threshold: float) -> np.ndarray:
    return (scores >= threshold).astype(int)


def metrics_for(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | int]:
    if len(y_true) == 0:
        return {
            "rows": 0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "accuracy": 0.0,
            "false_positive_rate": 0.0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "tp": 0,
        }
    labels = [0, 1]
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=labels).ravel()
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    return {
        "rows": int(len(y_true)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "false_positive_rate": float(fpr),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def train_one(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    feature_list: list[str],
    *,
    n_estimators: int,
    max_samples: str | int,
    percentile: float,
    random_state: int = RANDOM_STATE,
) -> tuple[IsolationForest, float, dict[str, Any]]:
    normal_train = train_df[train_df["label"].astype(int).eq(0)].copy()
    if normal_train.empty:
        raise ValueError("Train set không có normal window. Kiểm tra split_manifest.json.")
    x_train = prepare_x(normal_train, feature_list)
    model = IsolationForest(
        n_estimators=n_estimators,
        max_samples=max_samples,
        contamination="auto",
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(x_train)
    train_scores = anomaly_score(model, x_train)
    threshold = float(np.percentile(train_scores, percentile))

    x_val = prepare_x(validation_df, feature_list) if not validation_df.empty else pd.DataFrame(columns=feature_list)
    if validation_df.empty:
        val_pred = np.array([], dtype=int)
        val_true = np.array([], dtype=int)
    else:
        val_scores = anomaly_score(model, x_val)
        val_pred = predict_from_threshold(val_scores, threshold)
        val_true = validation_df["label"].fillna(0).astype(int).to_numpy()

    train_pred = predict_from_threshold(train_scores, threshold)
    train_true = np.zeros_like(train_pred)
    result = {
        "n_estimators": n_estimators,
        "max_samples": max_samples,
        "threshold_percentile": percentile,
        "threshold": threshold,
        "train_flagged_ratio": float(train_pred.mean()) if len(train_pred) else 0.0,
        "train_metrics": metrics_for(train_true, train_pred),
        "validation_metrics": metrics_for(val_true, val_pred),
    }
    return model, threshold, result


def tune_model(train_df: pd.DataFrame, validation_df: pd.DataFrame, feature_list: list[str]) -> tuple[IsolationForest, dict[str, Any], pd.DataFrame]:
    candidates: list[dict[str, Any]] = []
    best_model: IsolationForest | None = None
    best_result: dict[str, Any] | None = None
    best_key: tuple[float, float, float] | None = None

    for n_estimators in [100, 200, 300]:
        for max_samples in ["auto", 256]:
            for percentile in [90.0, 92.5, 95.0, 97.5]:
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
                    "max_samples": max_samples,
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


def save_artifact(
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
        "model_version": MODEL_VERSION,
        "dataset_version": DATASET_VERSION,
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
    parser = argparse.ArgumentParser(description="Train/tune Isolation Forest cho StudyDrive features.")
    parser.add_argument("--features-dir", default="data/processed/features_v1")
    parser.add_argument("--output-dir", default="artifacts/models/iforest_v1")
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
        model, result, tuning_df = tune_model(train_df, validation_df, feature_list)
        Path("artifacts/metrics").mkdir(parents=True, exist_ok=True)
        tuning_df.to_csv("artifacts/metrics/tuning_results.csv", index=False, encoding="utf-8-sig")
    else:
        model, threshold, result = train_one(
            train_df,
            validation_df,
            feature_list,
            n_estimators=args.n_estimators,
            max_samples=max_samples,
            percentile=args.threshold_percentile,
        )

    model_path = save_artifact(model, args.output_dir, feature_list, result, features_dir=args.features_dir)
    print("DONE train")
    print(f"  model: {model_path}")
    print(f"  threshold: {result['threshold']:.6f}")
    print(f"  validation: {result['validation_metrics']}")


if __name__ == "__main__":
    main()
