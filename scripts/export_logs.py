"""Export StudyDrive request logs to CSV.

Usage examples:
    python -m scripts.export_logs
    python -m scripts.export_logs --output data/raw/request_logs_raw.csv
    python -m scripts.export_logs --action-type export --sensitive yes
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func

from app import create_app
from app.models import RequestLog, User

CSV_COLUMNS = [
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


def parse_datetime(raw: str | None):
    if not raw:
        return None
    value = raw.strip()
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SystemExit(f"Datetime không hợp lệ: {raw}. Dùng YYYY-MM-DDTHH:MM:SS") from exc


def default_output_path() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    return Path("data/raw") / f"logs_{timestamp}.csv"


def build_query(args):
    query = RequestLog.query
    start = parse_datetime(args.start)
    end = parse_datetime(args.end)

    if start is not None:
        query = query.filter(RequestLog.timestamp >= start)
    if end is not None:
        query = query.filter(RequestLog.timestamp <= end)

    if args.user:
        user_value = args.user.strip()
        if user_value.isdigit():
            query = query.filter(RequestLog.user_id == int(user_value))
        else:
            pattern = f"%{user_value.lower()}%"
            query = query.outerjoin(User, RequestLog.user_id == User.id).filter(
                func.lower(User.username).like(pattern) | func.lower(User.email).like(pattern)
            )

    if args.action_type:
        query = query.filter(RequestLog.action_type == args.action_type)
    if args.status_code is not None:
        query = query.filter(RequestLog.status_code == args.status_code)
    if args.sensitive == "yes":
        query = query.filter(RequestLog.is_sensitive.is_(True))
    elif args.sensitive == "no":
        query = query.filter(RequestLog.is_sensitive.is_(False))
    if args.path_keyword:
        query = query.filter(RequestLog.path.like(f"%{args.path_keyword}%"))

    return query.order_by(RequestLog.timestamp.asc(), RequestLog.id.asc())


def log_to_row(log: RequestLog) -> dict[str, object]:
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


def export_logs(args) -> Path:
    output_path = Path(args.output) if args.output else default_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    app = create_app(args.config)
    with app.app_context():
        query = build_query(args)
        if args.limit:
            query = query.limit(args.limit)
        rows = query.all()

        with output_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for log in rows:
                writer.writerow(log_to_row(log))

    print(f"Đã export {len(rows)} log -> {output_path}")
    return output_path


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Export request_logs ra CSV an toàn.")
    parser.add_argument("--config", default="development", help="Tên config Flask")
    parser.add_argument("--output", help="Đường dẫn CSV; mặc định data/raw/logs_YYYYMMDD_HHMM.csv")
    parser.add_argument("--start", help="Lọc từ timestamp ISO")
    parser.add_argument("--end", help="Lọc đến timestamp ISO")
    parser.add_argument("--user", help="User id, username hoặc email")
    parser.add_argument("--action-type", dest="action_type")
    parser.add_argument("--status-code", type=int)
    parser.add_argument("--sensitive", choices=["all", "yes", "no"], default="all")
    parser.add_argument("--path-keyword")
    parser.add_argument("--limit", type=int)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    export_logs(parse_args(argv))


if __name__ == "__main__":
    main()
