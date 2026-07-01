"""Load an Isolation Forest artifact and detect anomalous StudyDrive windows.

CLI examples:
    python -m ml.detect --features data/processed/features_v1/test_features.csv
    python -m ml.detect --features data/processed/features_v1/features_all.csv --output artifacts/metrics/detect_all.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from ml.build_features import FEATURE_COLUMNS, validate_feature_matrix

DEFAULT_MODEL_PATH = "artifacts/models/iforest_v1/model.joblib"


def load_detector(model_path: str | Path = DEFAULT_MODEL_PATH) -> dict[str, Any]:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy model: {path}. Hãy chạy `python -m ml.train --tune` trước."
        )
    artifact = joblib.load(path)
    required = {"model", "feature_list", "threshold", "metadata"}
    if not required.issubset(set(artifact)):
        raise ValueError(f"Model artifact không đủ khóa {required}: {path}")
    return artifact


def prepare_features(df: pd.DataFrame, feature_list: list[str]) -> pd.DataFrame:
    validate_feature_matrix(df, feature_list)
    return df[feature_list].apply(pd.to_numeric, errors="coerce").fillna(0.0)


def anomaly_scores(artifact: dict[str, Any], feature_df: pd.DataFrame) -> np.ndarray:
    x = prepare_features(feature_df, artifact["feature_list"])
    return -artifact["model"].score_samples(x)


def scenario_hint_from_row(row: pd.Series) -> str:
    """Human-readable hint used for explanation only, not as a training label."""
    export_count = float(row.get("export_count", 0) or 0)
    delete_count = float(row.get("delete_count", 0) or 0)
    forbidden_rate = float(row.get("forbidden_rate", 0) or 0)
    not_found_rate = float(row.get("not_found_rate", 0) or 0)
    unique_failed = float(row.get("unique_failed_resource_id_count", 0) or 0)
    unique_resource = float(row.get("unique_resource_id_count", 0) or 0)
    sensitive_ratio = float(row.get("sensitive_ratio", 0) or 0)

    if export_count >= 3 or float(row.get("export_ratio", 0) or 0) >= 0.25:
        return "export_abuse"
    if delete_count >= 3 or float(row.get("delete_ratio", 0) or 0) >= 0.25:
        return "delete_abuse"
    if unique_failed >= 3 or forbidden_rate + not_found_rate >= 0.30:
        return "bola_scan"
    if unique_resource >= 8 and sensitive_ratio >= 0.20:
        return "resource_probe"
    return "general_anomaly"


def top_feature_deltas(row: pd.Series, feature_list: list[str], limit: int = 5) -> dict[str, float]:
    """Return top non-zero features for alert explanation.

    This is not SHAP. It is a simple, transparent display of the strongest raw
    feature values in the suspicious window.
    """
    values: dict[str, float] = {}
    for feature in feature_list:
        try:
            value = float(row.get(feature, 0) or 0)
        except Exception:
            value = 0.0
        if value != 0.0:
            values[feature] = value
    ordered = sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)[:limit]
    return dict(ordered)


def predict_feature_dataframe(feature_df: pd.DataFrame, artifact: dict[str, Any] | None = None, *, model_path: str | Path = DEFAULT_MODEL_PATH) -> pd.DataFrame:
    if feature_df.empty:
        return feature_df.copy()
    artifact = artifact or load_detector(model_path)
    scores = anomaly_scores(artifact, feature_df)
    threshold = float(artifact["threshold"])
    predictions = (scores >= threshold).astype(int)
    output = feature_df.copy()
    output["anomaly_score"] = scores
    output["threshold"] = threshold
    output["y_pred"] = predictions
    output["scenario_hint"] = [scenario_hint_from_row(row) if pred else "normal" for (_, row), pred in zip(output.iterrows(), predictions, strict=False)]
    output["top_features_json"] = [
        json.dumps(top_feature_deltas(row, artifact["feature_list"]), ensure_ascii=False)
        for _, row in output.iterrows()
    ]
    metadata = artifact.get("metadata", {})
    output["model_version"] = metadata.get("model_version", "iforest_v1")
    return output


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Detect anomalous windows from feature CSV.")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--features", default="data/processed/features_v1/test_features.csv")
    parser.add_argument("--output", default="artifacts/metrics/detect_predictions.csv")
    parser.add_argument("--only-anomalies", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    features = pd.read_csv(args.features, encoding="utf-8-sig")
    artifact = load_detector(args.model)
    predictions = predict_feature_dataframe(features, artifact)
    if args.only_anomalies:
        predictions = predictions[predictions["y_pred"].astype(int).eq(1)]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"DONE detect: {len(predictions)} rows -> {output_path}")


if __name__ == "__main__":
    main()
