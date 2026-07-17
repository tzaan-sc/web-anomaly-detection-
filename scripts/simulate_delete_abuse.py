"""Delete abuse simulator placeholder.

Simulate local Delete Abuse by soft-deleting many files owned by one user.
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from datetime import datetime, timezone

import requests

from scripts.simulator_common import (
    DEFAULT_BASE_URL,
    DEFAULT_PASSWORD,
    append_ground_truth,
    load_demo_user_data,
    login,
    make_run_id,
    post_with_csrf,
    request_with_timeout,
    sleep_random,
)

SEVERITY_DELETES = {"mild": 4, "medium": 10, "high": 18}


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Sinh Delete Abuse local bằng soft delete file của chính user.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="user2")
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--severity", choices=SEVERITY_DELETES, default="medium")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--seed", type=int, default=2026062702)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--ground-truth", default="data/raw/ground_truth.csv")
    parser.add_argument("--reset-after", action="store_true", help="Chạy reset_demo sau run thử nghiệm. Không dùng khi đang gom dataset vì sẽ xóa log.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    random.seed(args.seed)
    run_id = args.run_id or make_run_id("delete_abuse")
    user_data = load_demo_user_data(args.username, owned_limit=100)
    if not user_data.owned_file_ids:
        raise SystemExit(f"User {args.username} không có file active để xóa.")

    session = requests.Session()
    session.headers.update({"User-Agent": f"StudyDriveDeleteAbuseSimulator/{args.severity}"})
    started_at = datetime.now(timezone.utc)
    login(session, args.base_url, args.username, args.password)
    request_count = 2

    delete_count = min(SEVERITY_DELETES[args.severity], len(user_data.owned_file_ids))
    target_ids = random.sample(user_data.owned_file_ids, k=delete_count)

    for index, file_id in enumerate(target_ids, start=1):
        if index % 3 == 1:
            request_with_timeout(session, "GET", f"{args.base_url}/files")
            request_count += 1
        response = post_with_csrf(
            session,
            args.base_url,
            f"/files/{file_id}",
            post_path=f"/files/{file_id}/delete",
        )
        request_count += 2
        print(f"delete {index}/{delete_count}: file_id={file_id}, status={response.status_code}")
        sleep_random(fast=args.fast, low=0.05, high=0.3)

    request_with_timeout(session, "GET", f"{args.base_url}/trash")
    request_count += 1
    ended_at = datetime.now(timezone.utc)

    append_ground_truth(
        args.ground_truth,
        {
            "scenario_id": f"delete_abuse:{run_id}:{args.username}",
            "scenario": "delete_abuse",
            "label": 1,
            "run_id": run_id,
            "user_id": user_data.user_id,
            "username": args.username,
            "session_name": "delete_abuse",
            "severity": args.severity,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "request_count": request_count,
            "notes": f"soft deleted {delete_count} own files; target_ids={target_ids}",
        },
    )
    print(f"DONE delete_abuse run_id={run_id} -> {args.ground_truth}")

    if args.reset_after:
        print("reset-after bật: chạy python -m scripts.reset_demo để phục hồi demo. Lưu ý: log hiện tại cũng bị xóa nếu reset_demo xóa request_logs.")
        subprocess.run([sys.executable, "-m", "scripts.reset_demo"], check=True)


if __name__ == "__main__":
    main()
