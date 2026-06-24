"""Export a small semantic request-log sample for manual inspection.

Usage:
    python -m scripts.export_request_log_sample
    python -m scripts.export_request_log_sample --limit 50 --output samples/request_log_sample.csv
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from app import create_app
from app.models import RequestLog


DEFAULT_OUTPUT = Path("samples/request_log_sample.csv")

COLUMNS = [
    "id",
    "request_id",
    "timestamp",
    "user_id",
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


def row_to_dict(log: RequestLog) -> dict[str, object]:
    return {
        "id": log.id,
        "request_id": log.request_id,
        "timestamp": log.timestamp.isoformat() if log.timestamp else "",
        "user_id": log.user_id,
        "is_authenticated": int(bool(log.is_authenticated)),
        "role": log.role,
        "session_id_hash": log.session_id_hash,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "http_method": log.http_method,
        "endpoint": log.endpoint,
        "path": log.path,
        "action": log.action,
        "action_type": log.action_type,
        "is_sensitive": int(bool(log.is_sensitive)),
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "owner_id": log.owner_id,
        "permission": log.permission,
        "ownership_result": log.ownership_result,
        "authorization_result": log.authorization_result,
        "status_code": log.status_code,
        "response_time_ms": log.response_time_ms,
        "file_size": log.file_size,
        "export_item_count": log.export_item_count,
        "export_total_size": log.export_total_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export latest semantic request logs to CSV.")
    parser.add_argument("--limit", type=int, default=50, help="Number of latest rows to export.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output CSV path. Default: samples/request_log_sample.csv",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        rows = (
            RequestLog.query.order_by(RequestLog.id.desc())
            .limit(max(1, args.limit))
            .all()
        )
        # Export oldest to newest inside the sample for easier manual reading.
        rows = list(reversed(rows))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=COLUMNS)
        writer.writeheader()
        for log in rows:
            writer.writerow(row_to_dict(log))

    print(f"Exported {len(rows)} request logs to {args.output}")


if __name__ == "__main__":
    main()
