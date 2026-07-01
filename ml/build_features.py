"""Build StudyDrive anomaly-detection features from structured request logs.

Main command for week 4:
    python -m ml.build_features \
        --logs data/raw/request_logs_raw.csv \
        --ground-truth data/raw/ground_truth.csv \
        --output-dir data/processed/features_v1

The module is intentionally usable both as a CLI and as a library by the web
`detection_service`.  No label/scenario column is ever used as a model feature.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

DATASET_VERSION = "features_v1"
WINDOW_MINUTES = 5
RANDOM_SEED = 20260705

REQUIRED_LOG_COLUMNS = [
    "request_id",
    "timestamp",
    "user_id",
    "is_authenticated",
    "role",
    "session_id_hash",
    "http_method",
    "endpoint",
    "path",
    "action",
    "action_type",
    "is_sensitive",
    "resource_type",
    "resource_id",
    "ownership_result",
    "authorization_result",
    "status_code",
    "response_time_ms",
]

OPTIONAL_LOG_COLUMNS = [
    "id",
    "username",
    "ip_address",
    "user_agent",
    "owner_id",
    "permission",
    "file_size",
    "export_item_count",
    "export_total_size",
]

FEATURE_COLUMNS = [
    "request_count",
    "unique_endpoint_count",
    "unique_method_count",
    "session_duration_sec",
    "avg_inter_request_sec",
    "min_inter_request_sec",
    "burst_rate",
    "error_rate",
    "avg_response_time_ms",
    "sensitive_request_count",
    "sensitive_ratio",
    "export_count",
    "export_ratio",
    "delete_count",
    "delete_ratio",
    "unique_deleted_resource_count",
    "unique_resource_id_count",
    "resource_id_request_ratio",
    "forbidden_count",
    "forbidden_rate",
    "not_found_count",
    "not_found_rate",
    "unique_failed_resource_id_count",
    "resource_id_change_rate",
    "max_sensitive_streak",
]

IDENTIFIER_COLUMNS = [
    "window_id",
    "user_id",
    "session_id_hash",
    "window_start",
    "window_end",
    "label",
    "scenario",
    "run_id",
    "severity",
]


@dataclass(frozen=True)
class PipelineOutputs:
    clean_logs: pd.DataFrame
    window_mapping: pd.DataFrame
    features: pd.DataFrame
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    report: dict[str, object]


def _ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def file_sha256(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def validate_schema(df: pd.DataFrame, *, required: Iterable[str] = REQUIRED_LOG_COLUMNS) -> None:
    """Raise ValueError when required request-log columns are missing."""
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(
            "CSV log thiếu cột bắt buộc: " + ", ".join(missing) +
            ". Hãy export bằng scripts/export_logs.py hoặc trang Admin Logs."
        )


def load_logs(path: str | Path) -> pd.DataFrame:
    """Load request log CSV and validate the minimum schema."""
    df = _read_csv(Path(path))
    validate_schema(df)
    return df


def _to_bool_series(series: pd.Series) -> pd.Series:
    normalized = series.fillna(False).astype(str).str.strip().str.lower()
    return normalized.isin({"1", "true", "t", "yes", "y", "on"})


def _normalize_resource_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text


def clean_logs(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Normalize dtypes, remove duplicate request_id, and sort logs."""
    validate_schema(df)
    original_rows = int(len(df))
    work = df.copy()

    for column in OPTIONAL_LOG_COLUMNS:
        if column not in work.columns:
            work[column] = ""

    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce", utc=True)
    bad_timestamps = int(work["timestamp"].isna().sum())
    work = work.dropna(subset=["timestamp"])

    duplicate_request_id = int(work["request_id"].duplicated().sum())
    work = work.drop_duplicates(subset=["request_id"], keep="first")

    for column in ["user_id", "owner_id", "status_code", "file_size", "export_item_count", "export_total_size"]:
        if column in work.columns:
            work[column] = pd.to_numeric(work[column], errors="coerce")

    work["status_code"] = work["status_code"].fillna(0).astype(int)
    work["response_time_ms"] = pd.to_numeric(work["response_time_ms"], errors="coerce").fillna(0.0)
    work["is_authenticated"] = _to_bool_series(work["is_authenticated"])
    work["is_sensitive"] = _to_bool_series(work["is_sensitive"])

    fill_string_columns = [
        "role", "session_id_hash", "http_method", "endpoint", "path", "action",
        "action_type", "resource_type", "resource_id", "ownership_result",
        "authorization_result", "username", "ip_address", "user_agent", "permission",
    ]
    for column in fill_string_columns:
        if column in work.columns:
            work[column] = work[column].fillna("").astype(str).str.strip()

    work["resource_id"] = work["resource_id"].map(_normalize_resource_id)
    work["session_id_hash"] = work["session_id_hash"].replace("", "anonymous")
    work["user_id"] = work["user_id"].fillna(-1).astype(int)
    work["role"] = work["role"].replace("", "ANONYMOUS")
    work["action_type"] = work["action_type"].replace("", "other")
    work["http_method"] = work["http_method"].str.upper().replace("", "GET")

    work = work.sort_values(["user_id", "session_id_hash", "timestamp", "request_id"]).reset_index(drop=True)

    report = {
        "original_rows": original_rows,
        "rows_after_cleaning": int(len(work)),
        "dropped_bad_timestamp_rows": bad_timestamps,
        "dropped_duplicate_request_id_rows": duplicate_request_id,
        "timestamp_min": work["timestamp"].min().isoformat() if not work.empty else None,
        "timestamp_max": work["timestamp"].max().isoformat() if not work.empty else None,
    }
    return work, report


def _empty_ground_truth() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "scenario_id", "scenario", "label", "run_id", "user_id", "username",
            "session_name", "severity", "started_at", "ended_at", "request_count", "notes",
        ]
    )


def load_ground_truth(path: str | Path | None) -> pd.DataFrame:
    if path is None:
        return _empty_ground_truth()
    gt_path = Path(path)
    if not gt_path.exists() or gt_path.stat().st_size == 0:
        return _empty_ground_truth()
    gt = pd.read_csv(gt_path, encoding="utf-8-sig")
    for column in _empty_ground_truth().columns:
        if column not in gt.columns:
            gt[column] = ""
    gt["started_at"] = pd.to_datetime(gt["started_at"], errors="coerce", utc=True)
    gt["ended_at"] = pd.to_datetime(gt["ended_at"], errors="coerce", utc=True)
    gt["user_id"] = pd.to_numeric(gt["user_id"], errors="coerce").fillna(-1).astype(int)
    gt["label"] = pd.to_numeric(gt["label"], errors="coerce").fillna(0).astype(int)
    gt["scenario"] = gt["scenario"].fillna("normal").astype(str).str.strip().replace("", "normal")
    gt["run_id"] = gt["run_id"].fillna("unknown_run").astype(str).str.strip().replace("", "unknown_run")
    gt["severity"] = gt["severity"].fillna("").astype(str).str.strip()
    return gt.dropna(subset=["started_at", "ended_at"])


def attach_ground_truth(clean_df: pd.DataFrame, gt: pd.DataFrame) -> pd.DataFrame:
    """Attach log-level label/scenario by user and time overlap."""
    work = clean_df.copy()
    work["label"] = 0
    work["scenario"] = "normal"
    work["run_id"] = "unknown_run"
    work["severity"] = "normal"
    work["scenario_id"] = ""

    if gt.empty or work.empty:
        return work

    # Apply normal rows first and anomaly rows later, so anomaly wins when windows overlap.
    ordered_gt = gt.sort_values(["label", "started_at"])
    for row in ordered_gt.itertuples(index=False):
        mask = (
            (work["user_id"] == int(row.user_id))
            & (work["timestamp"] >= row.started_at)
            & (work["timestamp"] <= row.ended_at)
        )
        if not mask.any():
            continue
        work.loc[mask, "label"] = int(row.label)
        work.loc[mask, "scenario"] = str(row.scenario or "normal")
        work.loc[mask, "run_id"] = str(row.run_id or "unknown_run")
        work.loc[mask, "severity"] = str(row.severity or ("anomaly" if int(row.label) else "normal"))
        work.loc[mask, "scenario_id"] = str(row.scenario_id or "")

    return work


def make_window_id(user_id: int, session_id_hash: str, window_start: pd.Timestamp) -> str:
    base = f"{user_id}|{session_id_hash}|{window_start.isoformat()}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def assign_windows(logs: pd.DataFrame, *, window_minutes: int = WINDOW_MINUTES) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Assign every request to exactly one user/session/time window."""
    if logs.empty:
        empty = logs.copy()
        empty["window_start"] = pd.NaT
        empty["window_end"] = pd.NaT
        empty["window_id"] = ""
        return empty, pd.DataFrame(columns=["request_id", "window_id"])

    work = logs.copy()
    window_freq = f"{window_minutes}min"
    work["window_start"] = work["timestamp"].dt.floor(window_freq)
    work["window_end"] = work["window_start"] + pd.Timedelta(minutes=window_minutes)
    work["window_id"] = [
        make_window_id(int(user_id), str(session_id), window_start)
        for user_id, session_id, window_start in zip(
            work["user_id"], work["session_id_hash"], work["window_start"], strict=False
        )
    ]
    mapping = work[["request_id", "window_id", "timestamp", "user_id", "session_id_hash"]].copy()
    return work, mapping


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0 or pd.isna(denominator):
        return 0.0
    return float(numerator) / float(denominator)


def _max_true_streak(values: Iterable[bool]) -> int:
    best = 0
    current = 0
    for value in values:
        if bool(value):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return int(best)


def _resource_change_rate(resource_ids: Iterable[object]) -> float:
    values = [str(v) for v in resource_ids if str(v).strip()]
    if len(values) <= 1:
        return 0.0
    changes = sum(1 for prev, cur in zip(values, values[1:], strict=False) if prev != cur)
    return _safe_ratio(changes, len(values) - 1)


def _first_non_empty(values: pd.Series, default: str = "") -> str:
    for value in values:
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return default


def _window_label(values: pd.Series) -> int:
    return int(values.fillna(0).astype(int).max()) if len(values) else 0


def _window_scenario(group: pd.DataFrame) -> str:
    anomalies = group.loc[group["label"].astype(int) == 1, "scenario"].replace("", np.nan).dropna()
    if not anomalies.empty:
        return anomalies.value_counts().index[0]
    normal = group["scenario"].replace("", np.nan).dropna()
    return normal.value_counts().index[0] if not normal.empty else "normal"


def aggregate_features(windowed_logs: pd.DataFrame) -> pd.DataFrame:
    """Aggregate request logs into one ML row per user/session/5-minute window."""
    if windowed_logs.empty:
        return pd.DataFrame(columns=IDENTIFIER_COLUMNS + FEATURE_COLUMNS)

    records: list[dict[str, object]] = []
    grouped = windowed_logs.sort_values("timestamp").groupby("window_id", sort=False)
    for window_id, group in grouped:
        group = group.sort_values("timestamp")
        request_count = int(len(group))
        timestamp_delta = group["timestamp"].max() - group["timestamp"].min()
        session_duration_sec = max(float(timestamp_delta.total_seconds()), 0.0)
        inter_request = group["timestamp"].diff().dt.total_seconds().dropna()
        avg_inter = float(inter_request.mean()) if not inter_request.empty else 0.0
        min_inter = float(inter_request.min()) if not inter_request.empty else 0.0
        burst_rate = _safe_ratio(float((inter_request <= 1.0).sum()), len(inter_request))

        status = group["status_code"].fillna(0).astype(int)
        is_error = status >= 400
        is_forbidden = status == 403
        is_not_found = status == 404
        is_sensitive = group["is_sensitive"].fillna(False).astype(bool)
        action_type = group["action_type"].fillna("other").astype(str).str.lower()
        action = group["action"].fillna("").astype(str).str.lower()
        resource_id = group["resource_id"].fillna("").astype(str).str.strip()

        is_export = action_type.eq("export") | action.str.contains("export", na=False)
        is_delete = action_type.eq("delete") | action.str.contains("delete", na=False)
        failed_resource_ids = resource_id[(is_forbidden | is_not_found) & resource_id.ne("")]
        deleted_resource_ids = resource_id[is_delete & resource_id.ne("")]
        unique_resource_ids = resource_id[resource_id.ne("")].nunique()

        label = _window_label(group["label"] if "label" in group else pd.Series(dtype=int))
        scenario = _window_scenario(group) if "scenario" in group else "normal"
        run_id = _first_non_empty(group["run_id"] if "run_id" in group else pd.Series(dtype=str), "unknown_run")
        severity = _first_non_empty(group["severity"] if "severity" in group else pd.Series(dtype=str), "normal")

        record = {
            "window_id": window_id,
            "user_id": int(group["user_id"].iloc[0]),
            "session_id_hash": str(group["session_id_hash"].iloc[0]),
            "window_start": group["window_start"].iloc[0].isoformat(),
            "window_end": group["window_end"].iloc[0].isoformat(),
            "label": label,
            "scenario": scenario,
            "run_id": run_id,
            "severity": severity,
            "request_count": request_count,
            "unique_endpoint_count": int(group["endpoint"].nunique(dropna=True)),
            "unique_method_count": int(group["http_method"].nunique(dropna=True)),
            "session_duration_sec": session_duration_sec,
            "avg_inter_request_sec": avg_inter,
            "min_inter_request_sec": min_inter,
            "burst_rate": burst_rate,
            "error_rate": _safe_ratio(int(is_error.sum()), request_count),
            "avg_response_time_ms": float(group["response_time_ms"].mean()) if request_count else 0.0,
            "sensitive_request_count": int(is_sensitive.sum()),
            "sensitive_ratio": _safe_ratio(int(is_sensitive.sum()), request_count),
            "export_count": int(is_export.sum()),
            "export_ratio": _safe_ratio(int(is_export.sum()), request_count),
            "delete_count": int(is_delete.sum()),
            "delete_ratio": _safe_ratio(int(is_delete.sum()), request_count),
            "unique_deleted_resource_count": int(deleted_resource_ids.nunique()),
            "unique_resource_id_count": int(unique_resource_ids),
            "resource_id_request_ratio": _safe_ratio(int(unique_resource_ids), request_count),
            "forbidden_count": int(is_forbidden.sum()),
            "forbidden_rate": _safe_ratio(int(is_forbidden.sum()), request_count),
            "not_found_count": int(is_not_found.sum()),
            "not_found_rate": _safe_ratio(int(is_not_found.sum()), request_count),
            "unique_failed_resource_id_count": int(failed_resource_ids.nunique()),
            "resource_id_change_rate": _resource_change_rate(resource_id),
            "max_sensitive_streak": _max_true_streak(is_sensitive.tolist()),
        }
        records.append(record)

    features = pd.DataFrame.from_records(records)
    for column in FEATURE_COLUMNS:
        features[column] = pd.to_numeric(features[column], errors="coerce").replace([np.inf, -np.inf], 0).fillna(0.0)
    features = features.sort_values(["window_start", "user_id", "session_id_hash"]).reset_index(drop=True)
    return features


def split_features(features: pd.DataFrame, *, seed: int = RANDOM_SEED) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Split window-level features while keeping train normal-only and group-aware."""
    if features.empty:
        empty = features.copy()
        return empty, empty, empty, {"note": "features empty"}

    work = features.copy()
    work["_split_group"] = work["run_id"].fillna("unknown_run").astype(str)
    use_session_fallback = work["_split_group"].eq("unknown_run").all() or work["_split_group"].nunique() < 3
    if use_session_fallback:
        work["_split_group"] = work["user_id"].astype(str) + "|" + work["session_id_hash"].astype(str)

    group_summary = (
        work.groupby("_split_group")
        .agg(label=("label", "max"), first_window=("window_start", "min"), rows=("window_id", "count"))
        .sort_values("first_window")
        .reset_index()
    )

    normal_groups = group_summary.loc[group_summary["label"].eq(0), "_split_group"].tolist()
    anomaly_groups = group_summary.loc[group_summary["label"].eq(1), "_split_group"].tolist()

    rng = np.random.default_rng(seed)
    # Keep time order for normal if possible, but shuffle anomaly groups to spread scenarios.
    n_normal = len(normal_groups)
    train_cut = max(1, math.floor(n_normal * 0.60)) if n_normal else 0
    val_cut = max(train_cut + 1, math.floor(n_normal * 0.80)) if n_normal > 2 else train_cut

    train_groups = set(normal_groups[:train_cut])
    validation_groups = set(normal_groups[train_cut:val_cut])
    test_groups = set(normal_groups[val_cut:])

    anomaly_groups_shuffled = list(anomaly_groups)
    rng.shuffle(anomaly_groups_shuffled)
    for index, group in enumerate(anomaly_groups_shuffled):
        if index % 2 == 0:
            validation_groups.add(group)
        else:
            test_groups.add(group)

    # In tiny datasets, make sure val/test are not empty when possible.
    remaining_normal = [g for g in normal_groups if g not in train_groups]
    if not validation_groups and remaining_normal:
        validation_groups.add(remaining_normal[0])
    if not test_groups and len(remaining_normal) > 1:
        test_groups.add(remaining_normal[-1])
    if not test_groups and len(anomaly_groups_shuffled) > 1:
        candidate = anomaly_groups_shuffled[-1]
        validation_groups.discard(candidate)
        test_groups.add(candidate)

    def subset(groups: set[str]) -> pd.DataFrame:
        return work[work["_split_group"].isin(groups)].drop(columns=["_split_group"]).reset_index(drop=True)

    train = subset(train_groups)
    validation = subset(validation_groups)
    test = subset(test_groups)

    # Enforce train normal-only. Any anomaly accidentally present is moved to validation.
    train_anomaly = train[train["label"].astype(int).eq(1)]
    if not train_anomaly.empty:
        validation = pd.concat([validation, train_anomaly], ignore_index=True)
        train = train[train["label"].astype(int).eq(0)].reset_index(drop=True)

    manifest = {
        "dataset_version": DATASET_VERSION,
        "random_seed": seed,
        "split_group": "run_id" if not use_session_fallback else "user_id|session_id_hash",
        "train_groups": sorted(train_groups),
        "validation_groups": sorted(validation_groups),
        "test_groups": sorted(test_groups),
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "test_rows": int(len(test)),
        "train_anomaly_rows": int(train["label"].astype(int).sum()) if not train.empty else 0,
        "validation_anomaly_rows": int(validation["label"].astype(int).sum()) if not validation.empty else 0,
        "test_anomaly_rows": int(test["label"].astype(int).sum()) if not test.empty else 0,
    }
    return train, validation, test, manifest


def validate_feature_matrix(df: pd.DataFrame, feature_columns: list[str] = FEATURE_COLUMNS) -> None:
    missing = [c for c in feature_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Feature dataset thiếu cột: {missing}")
    matrix = df[feature_columns].apply(pd.to_numeric, errors="coerce")
    if matrix.isna().any().any():
        bad = matrix.columns[matrix.isna().any()].tolist()
        raise ValueError(f"Feature có NaN sau numeric conversion: {bad}")
    if not np.isfinite(matrix.to_numpy()).all():
        raise ValueError("Feature có inf/-inf. Hãy kiểm tra phép chia ratio.")


def write_feature_dictionary(output_path: str | Path) -> None:
    descriptions = {
        "request_count": "Số request trong cửa sổ.",
        "unique_endpoint_count": "Số endpoint khác nhau được gọi.",
        "unique_method_count": "Số HTTP method khác nhau.",
        "session_duration_sec": "Khoảng cách từ request đầu đến request cuối trong window.",
        "avg_inter_request_sec": "Khoảng cách trung bình giữa hai request liên tiếp.",
        "min_inter_request_sec": "Khoảng cách nhỏ nhất giữa hai request liên tiếp.",
        "burst_rate": "Tỷ lệ khoảng cách request <= 1 giây.",
        "error_rate": "Tỷ lệ status_code >= 400.",
        "avg_response_time_ms": "Thời gian xử lý trung bình.",
        "sensitive_request_count": "Số request nhạy cảm: export/delete/admin/detail trái quyền.",
        "sensitive_ratio": "Tỷ lệ request nhạy cảm.",
        "export_count": "Số request thuộc action export.",
        "export_ratio": "Tỷ lệ export trong window.",
        "delete_count": "Số request thuộc action delete.",
        "delete_ratio": "Tỷ lệ delete trong window.",
        "unique_deleted_resource_count": "Số resource_id khác nhau bị delete.",
        "unique_resource_id_count": "Số resource_id khác nhau xuất hiện.",
        "resource_id_request_ratio": "unique_resource_id_count / request_count.",
        "forbidden_count": "Số request trả 403.",
        "forbidden_rate": "Tỷ lệ request trả 403.",
        "not_found_count": "Số request trả 404.",
        "not_found_rate": "Tỷ lệ request trả 404.",
        "unique_failed_resource_id_count": "Số resource_id khác nhau trong request 403/404.",
        "resource_id_change_rate": "Tỷ lệ resource_id thay đổi giữa request liên tiếp.",
        "max_sensitive_streak": "Chuỗi request nhạy cảm liên tiếp dài nhất.",
    }
    lines = ["# Feature dictionary — features_v1", ""]
    lines.append("Các feature được tính ở cấp `user_id + session_id_hash + 5-minute window`.")
    lines.append("`label`, `scenario`, `run_id`, `timestamp` và các identifier không được đưa vào X_train.")
    lines.append("")
    lines.append("| Feature | Ý nghĩa |")
    lines.append("|---|---|")
    for feature in FEATURE_COLUMNS:
        lines.append(f"| `{feature}` | {descriptions.get(feature, '')} |")
    _ensure_parent(Path(output_path)).write_text("\n".join(lines), encoding="utf-8")


def build_pipeline(
    logs_path: str | Path,
    ground_truth_path: str | Path | None = None,
    *,
    output_dir: str | Path | None = None,
    window_minutes: int = WINDOW_MINUTES,
    seed: int = RANDOM_SEED,
) -> PipelineOutputs:
    logs_path = Path(logs_path)
    raw_df = load_logs(logs_path)
    clean_df, clean_report = clean_logs(raw_df)
    gt = load_ground_truth(ground_truth_path)
    labeled_logs = attach_ground_truth(clean_df, gt)
    windowed_logs, window_mapping = assign_windows(labeled_logs, window_minutes=window_minutes)
    features = aggregate_features(windowed_logs)
    validate_feature_matrix(features) if not features.empty else None
    train, validation, test, split_manifest = split_features(features, seed=seed)

    report = {
        "dataset_version": DATASET_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_logs_path": str(logs_path),
        "raw_logs_sha256": file_sha256(logs_path),
        "ground_truth_path": str(ground_truth_path) if ground_truth_path else None,
        "ground_truth_sha256": file_sha256(Path(ground_truth_path)) if ground_truth_path else None,
        "window_minutes": window_minutes,
        "feature_count": len(FEATURE_COLUMNS),
        "feature_columns": FEATURE_COLUMNS,
        "cleaning": clean_report,
        "window_count": int(len(features)),
        "label_distribution": features["label"].value_counts(dropna=False).to_dict() if not features.empty else {},
        "scenario_distribution": features["scenario"].value_counts(dropna=False).to_dict() if not features.empty else {},
        "split_manifest": split_manifest,
    }

    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        labeled_logs.to_csv(out / "clean_logs.csv", index=False, encoding="utf-8-sig")
        windowed_logs.to_csv(out / "windowed_logs.csv", index=False, encoding="utf-8-sig")
        window_mapping.to_csv(out / "window_mapping.csv", index=False, encoding="utf-8-sig")
        features.to_csv(out / "features_all.csv", index=False, encoding="utf-8-sig")
        train.to_csv(out / "train_features.csv", index=False, encoding="utf-8-sig")
        validation.to_csv(out / "validation_features.csv", index=False, encoding="utf-8-sig")
        test.to_csv(out / "test_features.csv", index=False, encoding="utf-8-sig")
        (out / "feature_list.json").write_text(json.dumps(FEATURE_COLUMNS, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "split_manifest.json").write_text(json.dumps(split_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "processing_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        write_feature_dictionary(out / "feature_dictionary.md")

    return PipelineOutputs(labeled_logs, window_mapping, features, train, validation, test, report)


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Build clean logs, windows, ML features and train/validation/test split.")
    parser.add_argument("--logs", default="data/raw/request_logs_raw.csv", help="CSV log xuất từ scripts/export_logs.py")
    parser.add_argument("--ground-truth", default="data/raw/ground_truth.csv", help="CSV ground truth từ simulator")
    parser.add_argument("--output-dir", default="data/processed/features_v1")
    parser.add_argument("--window-minutes", type=int, default=WINDOW_MINUTES)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    outputs = build_pipeline(
        args.logs,
        args.ground_truth,
        output_dir=args.output_dir,
        window_minutes=args.window_minutes,
        seed=args.seed,
    )
    print("DONE build_features")
    print(f"  clean logs: {len(outputs.clean_logs)} rows")
    print(f"  windows/features: {len(outputs.features)} rows")
    print(f"  train/val/test: {len(outputs.train)}/{len(outputs.validation)}/{len(outputs.test)}")
    print(f"  output: {args.output_dir}")


if __name__ == "__main__":
    main()
