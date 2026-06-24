"""Audit exported request log CSV with Pandas and write a markdown report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SENSITIVE_PATTERNS = [
    "password",
    "csrf_token",
    "session=",
    "remember_token",
    "cookie:",
    "SuperSecretPassword",
    "StudyDriveUser@2026",
    "StudyDriveAdmin@2026",
]


def audit(input_path: Path, output_path: Path) -> None:
    df = pd.read_csv(input_path)
    lines: list[str] = []
    lines.append("# Data audit — request logs")
    lines.append("")
    lines.append(f"- File: `{input_path}`")
    lines.append(f"- Audit time UTC: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- Shape: `{df.shape[0]}` rows × `{df.shape[1]}` columns")
    lines.append("")

    lines.append("## Dtype")
    lines.append("")
    lines.append("```text")
    lines.append(str(df.dtypes))
    lines.append("```")
    lines.append("")

    duplicate_request_id = int(df["request_id"].duplicated().sum()) if "request_id" in df else -1
    lines.append("## Quality checks")
    lines.append("")
    lines.append(f"- Duplicate request_id: `{duplicate_request_id}`")
    if "timestamp" in df:
        parsed_timestamp = pd.to_datetime(df["timestamp"], errors="coerce")
        lines.append(f"- Timestamp parse errors: `{int(parsed_timestamp.isna().sum())}`")
    if "response_time_ms" in df:
        response_numeric = pd.to_numeric(df["response_time_ms"], errors="coerce")
        lines.append(f"- response_time_ms numeric errors: `{int(response_numeric.isna().sum())}`")
    for column in ["is_authenticated", "is_sensitive"]:
        if column in df:
            values = sorted(df[column].dropna().astype(str).unique().tolist())
            lines.append(f"- `{column}` values: `{values}`")
    lines.append("")

    lines.append("## Null counts")
    lines.append("")
    lines.append("```text")
    lines.append(str(df.isna().sum()))
    lines.append("```")
    lines.append("")

    for column in ["action_type", "status_code", "user_id", "session_id_hash", "authorization_result"]:
        if column in df:
            lines.append(f"## Distribution: `{column}`")
            lines.append("")
            lines.append("```text")
            lines.append(str(df[column].fillna("<null>").value_counts().head(30)))
            lines.append("```")
            lines.append("")

    joined = "\n".join(df.astype(str).fillna("").agg(" ".join, axis=1).head(min(len(df), 10000)))
    leaked = [pattern for pattern in SENSITIVE_PATTERNS if pattern.lower() in joined.lower()]
    lines.append("## Sensitive-data scan")
    lines.append("")
    if leaked:
        lines.append(f"- FAIL: tìm thấy pattern nghi ngờ: `{leaked}`")
    else:
        lines.append("- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Đã ghi audit report -> {output_path}")


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Audit CSV request logs bằng Pandas.")
    parser.add_argument("--input", required=True, help="CSV log đã export")
    parser.add_argument("--output", default="docs/data_audit.md", help="File markdown audit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    audit(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
