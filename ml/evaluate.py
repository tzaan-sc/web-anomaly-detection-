"""Evaluate a trained StudyDrive Isolation Forest model on holdout test data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from ml.detect import DEFAULT_MODEL_PATH, load_detector, predict_feature_dataframe


def compute_metrics(df: pd.DataFrame) -> dict[str, object]:
    y_true = df["label"].fillna(0).astype(int).to_numpy()
    y_pred = df["y_pred"].fillna(0).astype(int).to_numpy()
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    metrics = {
        "rows": int(len(df)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "false_positive_rate": float(fpr),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }
    return metrics


def scenario_metrics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario, group in df.groupby("scenario", dropna=False):
        y_true = group["label"].fillna(0).astype(int).to_numpy()
        y_pred = group["y_pred"].fillna(0).astype(int).to_numpy()
        anomaly_rows = int(y_true.sum())
        detected = int(((y_true == 1) & (y_pred == 1)).sum())
        false_positive = int(((y_true == 0) & (y_pred == 1)).sum())
        rows.append(
            {
                "scenario": scenario or "unknown",
                "rows": int(len(group)),
                "anomaly_rows": anomaly_rows,
                "detected_anomaly_rows": detected,
                "detection_rate": detected / anomaly_rows if anomaly_rows else 0.0,
                "false_positive_rows": false_positive,
                "mean_score": float(group["anomaly_score"].mean()) if not group.empty else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values(["scenario"])


def plot_confusion_matrix(metrics: dict[str, object], output_path: Path) -> None:
    cm = metrics["confusion_matrix"]
    matrix = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(matrix)
    ax.set_xticks([0, 1], labels=["Pred normal", "Pred anomaly"])
    ax.set_yticks([0, 1], labels=["True normal", "True anomaly"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(matrix[i, j]), ha="center", va="center")
    ax.set_title("Confusion Matrix")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_score_distribution(predictions: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    normal = predictions[predictions["label"].fillna(0).astype(int).eq(0)]["anomaly_score"]
    anomaly = predictions[predictions["label"].fillna(0).astype(int).eq(1)]["anomaly_score"]
    ax.hist(normal, bins=30, alpha=0.65, label="normal")
    ax.hist(anomaly, bins=30, alpha=0.65, label="anomaly")
    threshold = predictions["threshold"].iloc[0] if "threshold" in predictions and not predictions.empty else None
    if threshold is not None:
        ax.axvline(float(threshold), linestyle="--", label="threshold")
    ax.set_title("Anomaly score distribution")
    ax.set_xlabel("anomaly_score (higher = more suspicious)")
    ax.set_ylabel("window count")
    ax.legend()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def evaluate(model_path: str | Path, test_features: str | Path, output_dir: str | Path) -> pd.DataFrame:
    artifact = load_detector(model_path)
    test_df = pd.read_csv(test_features, encoding="utf-8-sig")
    predictions = predict_feature_dataframe(test_df, artifact)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    metrics = compute_metrics(predictions)
    scenarios = scenario_metrics(predictions)

    predictions.to_csv(out / "test_predictions.csv", index=False, encoding="utf-8-sig")
    scenarios.to_csv(out / "scenario_metrics.csv", index=False, encoding="utf-8-sig")
    (out / "test_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    plot_confusion_matrix(metrics, out / "confusion_matrix.png")
    plot_score_distribution(predictions, out / "score_distribution.png")
    return predictions


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Evaluate model on holdout test_features.csv")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--test", default="data/processed/features_v1/test_features.csv")
    parser.add_argument("--output-dir", default="artifacts/metrics")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    predictions = evaluate(args.model, args.test, args.output_dir)
    print(f"DONE evaluate: {len(predictions)} predictions -> {args.output_dir}")


if __name__ == "__main__":
    main()
