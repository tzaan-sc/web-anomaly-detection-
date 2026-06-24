"""Simulate local IDOR/BOLA scan requests that the server must block."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timezone

import requests

from scripts.simulator_common import (
    DEFAULT_BASE_URL,
    DEFAULT_PASSWORD,
    append_ground_truth,
    load_demo_user_data,
    login,
    make_run_id,
    request_with_timeout,
    sleep_random,
)

MODE_COUNTS = {"low-and-slow": 18, "burst": 45}


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Sinh IDOR/BOLA scan local, chỉ nhận 403/404 từ server.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="user3")
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--mode", choices=MODE_COUNTS, default="burst")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--seed", type=int, default=2026062703)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--ground-truth", default="data/raw/ground_truth.csv")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    random.seed(args.seed)
    run_id = args.run_id or make_run_id("bola_scan")
    user_data = load_demo_user_data(args.username, other_limit=100)
    candidates = user_data.other_file_ids + user_data.missing_file_ids
    if not candidates:
        raise SystemExit("Không có file_id ứng viên để tạo BOLA scan.")

    session = requests.Session()
    session.headers.update({"User-Agent": f"StudyDriveBolaScanSimulator/{args.mode}"})
    started_at = datetime.now(timezone.utc)
    login(session, args.base_url, args.username, args.password)
    request_count = 2

    scan_count = min(MODE_COUNTS[args.mode], len(candidates))
    target_ids = random.sample(candidates, k=scan_count)

    for index, file_id in enumerate(target_ids, start=1):
        if index % 8 == 1:
            request_with_timeout(session, "GET", f"{args.base_url}/files")
            request_count += 1
        endpoint = random.choice([f"/api/files/{file_id}", f"/files/{file_id}", f"/files/{file_id}/download"])
        response = request_with_timeout(session, "GET", f"{args.base_url}{endpoint}", allow_redirects=False)
        request_count += 1
        print(f"scan {index}/{scan_count}: {endpoint} -> {response.status_code}")
        if args.mode == "low-and-slow":
            sleep_random(fast=args.fast, low=1.5, high=4.0)
        else:
            sleep_random(fast=args.fast, low=0.03, high=0.18)

    ended_at = datetime.now(timezone.utc)
    append_ground_truth(
        args.ground_truth,
        {
            "scenario_id": f"bola_scan:{run_id}:{args.username}",
            "scenario": "bola_scan",
            "label": 1,
            "run_id": run_id,
            "user_id": user_data.user_id,
            "username": args.username,
            "session_name": args.mode,
            "severity": "medium" if args.mode == "low-and-slow" else "high",
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "request_count": request_count,
            "notes": f"tried {scan_count} other/missing file ids; server must keep returning 404/denied without data leak",
        },
    )
    print(f"DONE bola_scan run_id={run_id} -> {args.ground_truth}")


if __name__ == "__main__":
    main()
