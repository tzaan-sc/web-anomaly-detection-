"""Web integration service for StudyDrive anomaly detection.

This service reads RequestLog rows, builds the same window-level features used by
`ml.build_features`, loads the trained Isolation Forest artifact, and stores
anomaly alerts.  It is deliberately batch/on-demand to match the project scope.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
from sqlalchemy import and_

from app.extensions import db
from app.models import Alert, RequestLog
from ml.build_features import aggregate_features, assign_windows, clean_logs
from ml.detect import DEFAULT_MODEL_PATH, load_detector, predict_feature_dataframe


@dataclass(frozen=True)
class DetectionRunResult:
    ok: bool
    message: str
    windows_scored: int = 0
    anomalies_found: int = 0
    alerts_created: int = 0
    alerts_skipped_duplicate: int = 0
    model_version: str | None = None


LOG_COLUMNS = [
    "id",
    "request_id",
    "timestamp",
    "user_id",
    "username",
    "is_authenticated",
    "role",
    "session_id_hash",
    "ip_address",
    "user_agent",
    "http_method",
    "endpoint",
    "path",
    "action",
    "action_type",
    "is_sensitive",
    "resource_type",
    "resource_id",
    "owner_id",
    "permission",
    "ownership_result",
    "authorization_result",
    "status_code",
    "response_time_ms",
    "file_size",
    "export_item_count",
    "export_total_size",
]


def _log_to_dict(log: RequestLog) -> dict[str, object]:
    return {
        "id": log.id,
        "request_id": log.request_id,
        "timestamp": log.timestamp.isoformat() if log.timestamp else "",
        "user_id": log.user_id if log.user_id is not None else "",
        "username": log.user.username if log.user else "",
        "is_authenticated": int(bool(log.is_authenticated)),
        "role": log.role or "",
        "session_id_hash": log.session_id_hash or "",
        "ip_address": log.ip_address or "",
        "user_agent": log.user_agent or "",
        "http_method": log.http_method or "",
        "endpoint": log.endpoint or "",
        "path": log.path or "",
        "action": log.action or "",
        "action_type": log.action_type or "",
        "is_sensitive": int(bool(log.is_sensitive)),
        "resource_type": log.resource_type or "",
        "resource_id": log.resource_id or "",
        "owner_id": log.owner_id if log.owner_id is not None else "",
        "permission": log.permission or "",
        "ownership_result": log.ownership_result or "",
        "authorization_result": log.authorization_result or "",
        "status_code": log.status_code,
        "response_time_ms": log.response_time_ms,
        "file_size": log.file_size if log.file_size is not None else "",
        "export_item_count": log.export_item_count if log.export_item_count is not None else "",
        "export_total_size": log.export_total_size if log.export_total_size is not None else "",
    }


def query_logs(start: datetime | None = None, end: datetime | None = None, limit: int | None = None) -> list[RequestLog]:
    query = RequestLog.query
    if start is not None:
        query = query.filter(RequestLog.timestamp >= start)
    if end is not None:
        query = query.filter(RequestLog.timestamp <= end)
    query = query.order_by(RequestLog.timestamp.asc(), RequestLog.id.asc())
    if limit:
        query = query.limit(limit)
    return query.all()


def request_logs_to_dataframe(logs: Iterable[RequestLog]) -> pd.DataFrame:
    rows = [_log_to_dict(log) for log in logs]
    if not rows:
        return pd.DataFrame(columns=LOG_COLUMNS)
    return pd.DataFrame(rows, columns=LOG_COLUMNS)


def build_features_from_logs_dataframe(log_df: pd.DataFrame) -> pd.DataFrame:
    if log_df.empty:
        return pd.DataFrame()
    clean_df, _report = clean_logs(log_df)
    clean_df["label"] = 0
    clean_df["scenario"] = "unknown"
    clean_df["run_id"] = "web_detection"
    clean_df["severity"] = "unknown"
    windowed, _mapping = assign_windows(clean_df)
    return aggregate_features(windowed)


def _parse_window_time(value: object):
    try:
        return pd.to_datetime(value, utc=True).to_pydatetime()
    except Exception:
        return datetime.utcnow()


def _features_for_alert(row: pd.Series) -> str:
    if "top_features_json" in row and row["top_features_json"]:
        try:
            top_features = json.loads(row["top_features_json"])
        except Exception:
            top_features = {}
    else:
        top_features = {}
    payload = {
        "top_features": top_features,
        "request_count": float(row.get("request_count", 0) or 0),
        "error_rate": float(row.get("error_rate", 0) or 0),
        "sensitive_ratio": float(row.get("sensitive_ratio", 0) or 0),
        "export_count": float(row.get("export_count", 0) or 0),
        "delete_count": float(row.get("delete_count", 0) or 0),
        "forbidden_rate": float(row.get("forbidden_rate", 0) or 0),
        "not_found_rate": float(row.get("not_found_rate", 0) or 0),
        "unique_resource_id_count": float(row.get("unique_resource_id_count", 0) or 0),
    }
    return json.dumps(payload, ensure_ascii=False)


def run_detection(
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    limit: int | None = None,
) -> DetectionRunResult:
    """Run detection over current DB logs and persist Alert rows."""
    path = Path(model_path)
    if not path.exists():
        return DetectionRunResult(False, f"Chưa có model tại {path}. Hãy train trước.")

    logs = query_logs(start=start, end=end, limit=limit)
    if not logs:
        return DetectionRunResult(False, "Không có request log trong khoảng đã chọn.")

    log_df = request_logs_to_dataframe(logs)
    features = build_features_from_logs_dataframe(log_df)
    if features.empty:
        return DetectionRunResult(False, "Không tạo được feature window từ log.")

    try:
        artifact = load_detector(path)
        predictions = predict_feature_dataframe(features, artifact)
    except Exception as exc:
        return DetectionRunResult(False, f"Detection lỗi: {exc}")

    model_version = artifact.get("metadata", {}).get("model_version", "iforest_v1")
    anomaly_rows = predictions[predictions["y_pred"].astype(int).eq(1)].copy()
    created = 0
    skipped = 0

    for _, row in anomaly_rows.iterrows():
        window_id = str(row["window_id"])
        exists = Alert.query.filter_by(window_id=window_id, model_version=model_version).first()
        if exists is not None:
            skipped += 1
            continue

        alert = Alert(
            user_id=int(row["user_id"]) if int(row["user_id"]) >= 0 else None,
            window_id=window_id,
            window_start=_parse_window_time(row["window_start"]),
            window_end=_parse_window_time(row["window_end"]),
            model_version=model_version,
            anomaly_score=float(row["anomaly_score"]),
            scenario_hint=str(row.get("scenario_hint") or "general_anomaly"),
            features_json=_features_for_alert(row),
            status="NEW",
        )
        db.session.add(alert)
        created += 1

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return DetectionRunResult(
        True,
        "Detection chạy xong.",
        windows_scored=int(len(predictions)),
        anomalies_found=int(len(anomaly_rows)),
        alerts_created=created,
        alerts_skipped_duplicate=skipped,
        model_version=model_version,
    )


def alert_log_filter_url_args(alert: Alert) -> dict[str, object]:
    return {
        "user": alert.user_id or "",
        "start": alert.window_start.isoformat() if alert.window_start else "",
        "end": alert.window_end.isoformat() if alert.window_end else "",
        "sort": "newest",
    }
