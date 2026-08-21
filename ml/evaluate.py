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
    tn, fp, fn, tp = cm["tn"], cm["fp"], cm["fn"], cm["tp"]
    
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=300)
    im = ax.imshow(matrix, cmap="Blues", interpolation="nearest")
    
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Dự đoán\nNormal (0)", "Dự đoán\nAnomaly (1)"], fontsize=11, fontweight="600")
    ax.set_yticklabels(["Thực tế\nNormal (0)", "Thực tế\nAnomaly (1)"], fontsize=11, fontweight="600")
    
    cell_texts = [
        [f"TN = {tn}\n(Đúng Normal)", f"FP = {fp}\n(Báo nhầm)"],
        [f"FN = {fn}\n(Bỏ sót)", f"TP = {tp}\n(Bắt đúng Anomaly)"],
    ]
    for i in range(2):
        for j in range(2):
            val = matrix[i, j]
            color = "white" if val >= max(2, int(matrix.max() * 0.6)) else "#1e293b"
            ax.text(j, i, cell_texts[i][j], ha="center", va="center", fontsize=11, fontweight="bold", color=color)
            
    ax.set_title("Ma Trận Nhầm Lẫn (Confusion Matrix)", fontsize=13, fontweight="bold", pad=12, color="#1e293b")
    ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_score_distribution(predictions: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    normal = predictions[predictions["label"].fillna(0).astype(int).eq(0)]["anomaly_score"]
    anomaly = predictions[predictions["label"].fillna(0).astype(int).eq(1)]["anomaly_score"]
    threshold = float(predictions["threshold"].iloc[0]) if "threshold" in predictions and not predictions.empty else None

    all_scores = predictions["anomaly_score"]
    bins = np.linspace(all_scores.min() - 0.01, all_scores.max() + 0.01, 20)

    if not normal.empty:
        ax.hist(normal, bins=bins, alpha=0.65, color="#2563eb", label=f"Normal (n={len(normal)})", edgecolor="#1d4ed8")
    if not anomaly.empty:
        ax.hist(anomaly, bins=bins, alpha=0.65, color="#dc2626", label=f"Anomaly (n={len(anomaly)})", edgecolor="#b91c1c")
        
    if threshold is not None:
        ax.axvline(float(threshold), color="#111827", linestyle="--", linewidth=2.2, label=f"Ngưỡng (Threshold = {threshold:.4f})")

    ax.set_title("Phân Phối Điểm Bất Thường (Score Distribution)", fontsize=13, fontweight="bold", pad=12, color="#1e293b")
    ax.set_xlabel("Anomaly Score (Cao hơn = Bất thường hơn)", fontsize=11, fontweight="600")
    ax.set_ylabel("Số lượng cửa sổ (Windows)", fontsize=11, fontweight="600")
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", fontsize=10, loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
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
    out = Path(args.output_dir)
    metrics_path = out / "test_metrics.json"
    
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        cm = metrics.get("confusion_matrix", {})
        print("\n" + "=" * 60)
        print("=== EVALUATION RESULTS (TEST SET METRICS) ===")
        print("=" * 60)
        print(f"  • Total Test Samples       : {metrics.get('rows', len(predictions))}")
        print(f"  • Accuracy (Do chinh xac)  : {metrics.get('accuracy', 0.0)*100:.2f}%")
        print(f"  • Precision (Do chinh xac) : {metrics.get('precision', 0.0)*100:.2f}%")
        print(f"  • Recall (Ty le bat trung) : {metrics.get('recall', 0.0)*100:.2f}%")
        print(f"  • F1-Score                 : {metrics.get('f1', 0.0):.4f}")
        print(f"  • False Positive Rate (FPR): {metrics.get('false_positive_rate', 0.0)*100:.2f}%")
        print("-" * 60)
        print(f"  • Confusion Matrix: TN={cm.get('tn', 0)} | FP={cm.get('fp', 0)} | FN={cm.get('fn', 0)} | TP={cm.get('tp', 0)}")
        print("=" * 60)
        print(f" Saved metrics & plots to: {args.output_dir}\n")


if __name__ == "__main__":
    main()
