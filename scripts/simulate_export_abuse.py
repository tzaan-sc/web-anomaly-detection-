"""Simulate local Export Abuse against StudyDrive demo data."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timezone

import requests

from scripts.simulator_common import (
    DEFAULT_BASE_URL,
    DEFAULT_PASSWORD,
    append_ground_truth,
    choose_file_id,
    load_demo_user_data,
    login,
    make_run_id,
    post_with_csrf,
    request_with_timeout,
    sleep_random,
)

SEVERITY_EXPORTS = {"mild": 5, "medium": 12, "high": 25}


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Sinh Export Abuse local, an toàn và tái lập.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="user1")
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--severity", choices=SEVERITY_EXPORTS, default="medium")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--seed", type=int, default=20260627)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--ground-truth", default="data/raw/ground_truth.csv")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    random.seed(args.seed)
    run_id = args.run_id or make_run_id("export_abuse")
    user_data = load_demo_user_data(args.username)
    session = requests.Session()
    session.headers.update({"User-Agent": f"StudyDriveExportAbuseSimulator/{args.severity}"})
    started_at = datetime.now(timezone.utc)
    login(session, args.base_url, args.username, args.password)
    request_count = 2

    export_count = SEVERITY_EXPORTS[args.severity]
    for i in range(export_count):
        if i % 3 == 0:
            request_with_timeout(session, "GET", f"{args.base_url}/files")
            request_count += 1
        if i % 4 == 0:
            file_id = choose_file_id(user_data.owned_file_ids)
            if file_id:
                request_with_timeout(session, "GET", f"{args.base_url}/files/{file_id}")
                request_count += 1
        # Repeated metadata export is the suspicious behavior.
        response = post_with_csrf(
            session,
            args.base_url,
            "/files",
            post_path="/files/export",
            data={"q": "", "extension": "", "folder": ""},
        )
        request_count += 2
        print(f"export {i + 1}/{export_count}: status={response.status_code}")
        sleep_random(fast=args.fast, low=0.05, high=0.35)

    ended_at = datetime.now(timezone.utc)
    append_ground_truth(
        args.ground_truth,
        {
            "scenario_id": f"export_abuse:{run_id}:{args.username}",
            "scenario": "export_abuse",
            "label": 1,
            "run_id": run_id,
            "user_id": user_data.user_id,
            "username": args.username,
            "session_name": "export_abuse",
            "severity": args.severity,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "request_count": request_count,
            "notes": f"{export_count} repeated CSV metadata exports mixed with normal browsing",
        },
    )
    print(f"DONE export_abuse run_id={run_id} -> {args.ground_truth}")


if __name__ == "__main__":
    main()
