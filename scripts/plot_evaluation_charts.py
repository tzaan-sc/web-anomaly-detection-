"""Generate high-resolution, beautiful Vietnamese evaluation charts for PPT/Report.

Outputs saved to:
    artifacts/figures/confusion_matrix_vn.png
    artifacts/figures/score_distribution_vn.png
    artifacts/figures/evaluation_dashboard_slide.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

# Set clean aesthetic style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

PREDICTIONS_PATH = Path("artifacts/metrics/test_predictions.csv")
OUTPUT_DIR = Path("artifacts/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_custom_confusion_matrix(df: pd.DataFrame, out_path: Path):
    y_true = df["label"].fillna(0).astype(int).to_numpy()
    y_pred = df["y_pred"].fillna(0).astype(int).to_numpy()
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=300)
    
    # Custom color matrix
    im = ax.imshow(cm, cmap="Blues", interpolation="nearest")
    
    # Tick labels
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Dự đoán\nNormal (0)", "Dự đoán\nAnomaly (1)"], fontsize=11, fontweight="600")
    ax.set_yticklabels(["Thực tế\nNormal (0)", "Thực tế\nAnomaly (1)"], fontsize=11, fontweight="600")
    
    # Cell descriptions
    cell_texts = [
        [f"TN = {tn}\n(Đúng: Normal)", f"FP = {fp}\n(Báo nhầm)"],
        [f"FN = {fn}\n(Bỏ sót)", f"TP = {tp}\n(Bắt đúng Anomaly)"]
    ]
    
    for i in range(2):
        for j in range(2):
            val = cm[i, j]
            color = "white" if val >= 2 else "#1a252f"
            ax.text(
                j, i, cell_texts[i][j],
                ha="center", va="center",
                fontsize=12, fontweight="bold",
                color=color
            )

    ax.set_title("Ma Trận Nhầm Lẫn (Confusion Matrix - Test Set)", fontsize=13, fontweight="bold", pad=15, color="#1e293b")
    ax.grid(False)
    
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=10)
    
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f" Saved: {out_path}")


def plot_custom_score_distribution(df: pd.DataFrame, out_path: Path):
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)

    normal_scores = df[df["label"].eq(0)]["anomaly_score"]
    anomaly_scores = df[df["label"].eq(1)]["anomaly_score"]
    threshold = float(df["threshold"].iloc[0]) if "threshold" in df.columns else 0.4866

    # Plot scatter & bars
    bins = np.linspace(df["anomaly_score"].min() - 0.01, df["anomaly_score"].max() + 0.01, 15)
    
    ax.hist(normal_scores, bins=bins, alpha=0.65, color="#2563eb", label=f"Normal (n={len(normal_scores)})", edgecolor="#1d4ed8")
    ax.hist(anomaly_scores, bins=bins, alpha=0.65, color="#dc2626", label=f"Anomaly (n={len(anomaly_scores)})", edgecolor="#b91c1c")

    # Threshold line
    ax.axvline(threshold, color="#111827", linestyle="--", linewidth=2.2, label=f"Ngưỡng (Threshold = {threshold:.4f})")

    ax.set_title("Phân Phối Điểm Bất Thường (Anomaly Score Distribution - Test Set)", fontsize=13, fontweight="bold", pad=12, color="#1e293b")
    ax.set_xlabel("Anomaly Score (Điểm càng cao -> Càng bất thường)", fontsize=11, fontweight="600")
    ax.set_ylabel("Số lượng cửa sổ (Windows)", fontsize=11, fontweight="600")
    
    ax.legend(frameon=True, facecolor="white", edgecolor="#e2e8f0", fontsize=10, loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f" Saved: {out_path}")


def plot_combined_slide_dashboard(df: pd.DataFrame, out_path: Path):
    """Combine both charts into a single wide slide-ready image."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    # 1. Left: Confusion Matrix
    y_true = df["label"].fillna(0).astype(int).to_numpy()
    y_pred = df["y_pred"].fillna(0).astype(int).to_numpy()
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    im = ax1.imshow(cm, cmap="Blues", interpolation="nearest")
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(["Dự đoán Normal", "Dự đoán Anomaly"], fontsize=11, fontweight="600")
    ax1.set_yticklabels(["Thực tế Normal", "Thực tế Anomaly"], fontsize=11, fontweight="600")

    cell_texts = [
        [f"TN = {tn}\n(Đúng Normal)", f"FP = {fp}\n(Báo nhầm)"],
        [f"FN = {fn}\n(Bỏ sót)", f"TP = {tp}\n(Bắt đúng Anomaly)"]
    ]
    for i in range(2):
        for j in range(2):
            val = cm[i, j]
            color = "white" if val >= 2 else "#1e293b"
            ax1.text(j, i, cell_texts[i][j], ha="center", va="center", fontsize=11, fontweight="bold", color=color)
    ax1.set_title("A. Confusion Matrix (Tập Test)", fontsize=12, fontweight="bold", pad=12)
    ax1.grid(False)

    # 2. Right: Score Distribution
    normal_scores = df[df["label"].eq(0)]["anomaly_score"]
    anomaly_scores = df[df["label"].eq(1)]["anomaly_score"]
    threshold = float(df["threshold"].iloc[0]) if "threshold" in df.columns else 0.4866

    bins = np.linspace(df["anomaly_score"].min() - 0.01, df["anomaly_score"].max() + 0.01, 15)
    ax2.hist(normal_scores, bins=bins, alpha=0.65, color="#2563eb", label=f"Normal ({len(normal_scores)})", edgecolor="#1d4ed8")
    ax2.hist(anomaly_scores, bins=bins, alpha=0.65, color="#dc2626", label=f"Anomaly ({len(anomaly_scores)})", edgecolor="#b91c1c")
    ax2.axvline(threshold, color="#111827", linestyle="--", linewidth=2.2, label=f"Ngưỡng = {threshold:.4f}")

    ax2.set_title("B. Phân Phối Điểm Anomaly Score (Tập Test)", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlabel("Anomaly Score (Cao hơn = Bất thường hơn)", fontsize=11, fontweight="600")
    ax2.set_ylabel("Số lượng cửa sổ (Windows)", fontsize=11, fontweight="600")
    ax2.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("ĐÁNH GIÁ HIỆU NĂNG MÔ HÌNH TRÊN TẬP KIỂM THỬ ĐỘC LẬP (TEST SET)", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f" Saved Combined Slide: {out_path}")


def main():
    if not PREDICTIONS_PATH.exists():
        print(f"Error: {PREDICTIONS_PATH} does not exist. Run `python -m ml.evaluate` first.")
        return

    df = pd.read_csv(PREDICTIONS_PATH, encoding="utf-8-sig")
    print(f"Loaded {len(df)} predictions from {PREDICTIONS_PATH}")

    plot_custom_confusion_matrix(df, OUTPUT_DIR / "confusion_matrix_vn.png")
    plot_custom_score_distribution(df, OUTPUT_DIR / "score_distribution_vn.png")
    plot_combined_slide_dashboard(df, OUTPUT_DIR / "evaluation_dashboard_slide.png")
    print("\n Done generating all charts!")


if __name__ == "__main__":
    main()
