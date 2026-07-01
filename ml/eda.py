"""Create simple EDA charts and notes for features_v1."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

EDA_FEATURES = [
    "request_count",
    "export_count",
    "delete_count",
    "forbidden_rate",
    "unique_resource_id_count",
]


def plot_histogram(df: pd.DataFrame, feature: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    for label_value, name in [(0, "normal"), (1, "anomaly")]:
        subset = df[df["label"].fillna(0).astype(int).eq(label_value)]
        if not subset.empty:
            ax.hist(subset[feature], bins=30, alpha=0.65, label=name)
    ax.set_title(f"Histogram: {feature}")
    ax.set_xlabel(feature)
    ax.set_ylabel("window count")
    ax.legend()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def write_notes(df: pd.DataFrame, output_path: Path) -> None:
    lines = ["# EDA notes — features_v1", ""]
    lines.append(f"- Tổng số window: `{len(df)}`")
    lines.append("- Phân bố label:")
    lines.append("```text")
    lines.append(str(df["label"].fillna(0).astype(int).value_counts()))
    lines.append("```")
    lines.append("")
    lines.append("## Mean/median theo scenario")
    lines.append("")
    if not df.empty:
        summary = df.groupby("scenario")[EDA_FEATURES].agg(["mean", "median", "max"]).round(3)
        lines.append("```text")
        lines.append(str(summary))
        lines.append("```")
    lines.append("")
    constant = [c for c in EDA_FEATURES if c in df.columns and df[c].nunique(dropna=False) <= 1]
    lines.append(f"- Feature gần như constant trong nhóm EDA: `{constant}`")
    lines.append("- Không tối ưu theo test set; biểu đồ chỉ dùng để kiểm tra lỗi feature và giải thích báo cáo.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_eda(features_path: str | Path, output_dir: str | Path) -> None:
    df = pd.read_csv(features_path, encoding="utf-8-sig")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for feature in EDA_FEATURES:
        if feature in df.columns:
            plot_histogram(df, feature, out / f"hist_{feature}.png")
    write_notes(df, out / "eda_notes.md")
    print(f"DONE EDA -> {out}")


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Generate EDA figures for features_v1")
    parser.add_argument("--features", default="data/processed/features_v1/features_all.csv")
    parser.add_argument("--output-dir", default="artifacts/figures/eda_features_v1")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    run_eda(args.features, args.output_dir)


if __name__ == "__main__":
    main()
