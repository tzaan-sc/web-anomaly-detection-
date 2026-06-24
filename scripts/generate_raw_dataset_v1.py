"""Orchestrate raw dataset v1 generation from normal + anomaly simulators.

Run this while the Flask server is already running locally:
    python run.py

Then in another terminal:
    python -m scripts.generate_raw_dataset_v1 --fast --normal-requests 5000
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

from scripts.simulator_common import DEFAULT_BASE_URL, make_run_id, write_generation_metadata


def run_command(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def assert_server(base_url: str) -> None:
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
    except Exception as exc:
        raise SystemExit(
            f"Server chưa chạy hoặc /health lỗi tại {base_url}. Hãy chạy `python run.py` trước."
        ) from exc


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Sinh raw dataset v1 5.000–10.000 log.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--skip-reset", action="store_true", help="Không reset DB trước khi sinh dữ liệu")
    parser.add_argument("--normal-requests", type=int, default=5000)
    parser.add_argument("--raw-output", default="data/raw/request_logs_raw.csv")
    parser.add_argument("--ground-truth", default="data/raw/ground_truth.csv")
    parser.add_argument("--metadata", default="data/raw/generation_metadata.json")
    parser.add_argument("--audit-output", default="docs/data_audit.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    assert_server(args.base_url)

    run_id = make_run_id("raw_v1")
    started_at = datetime.now(timezone.utc)
    Path(args.ground_truth).parent.mkdir(parents=True, exist_ok=True)
    if Path(args.ground_truth).exists():
        Path(args.ground_truth).unlink()

    if not args.skip_reset:
        run_command([sys.executable, "-m", "scripts.reset_demo"])

    fast_flag = ["--fast"] if args.fast else []

    run_command([
        sys.executable,
        "-m",
        "scripts.simulate_normal",
        "--base-url",
        args.base_url,
        "--users",
        "user1,user2,user3,user4,user5",
        "--requests",
        str(args.normal_requests),
        "--run-id",
        run_id,
        "--ground-truth",
        args.ground_truth,
        *fast_flag,
    ])

    for severity, username in [("mild", "user1"), ("medium", "user2"), ("high", "user3")]:
        run_command([
            sys.executable,
            "-m",
            "scripts.simulate_export_abuse",
            "--base-url",
            args.base_url,
            "--username",
            username,
            "--severity",
            severity,
            "--run-id",
            run_id,
            "--ground-truth",
            args.ground_truth,
            *fast_flag,
        ])

    for severity, username in [("mild", "user4"), ("medium", "user5")]:
        run_command([
            sys.executable,
            "-m",
            "scripts.simulate_delete_abuse",
            "--base-url",
            args.base_url,
            "--username",
            username,
            "--severity",
            severity,
            "--run-id",
            run_id,
            "--ground-truth",
            args.ground_truth,
            *fast_flag,
        ])

    for mode, username in [("low-and-slow", "user1"), ("burst", "user2")]:
        run_command([
            sys.executable,
            "-m",
            "scripts.simulate_bola_scan",
            "--base-url",
            args.base_url,
            "--username",
            username,
            "--mode",
            mode,
            "--run-id",
            run_id,
            "--ground-truth",
            args.ground_truth,
            *fast_flag,
        ])

    run_command([
        sys.executable,
        "-m",
        "scripts.export_logs",
        "--output",
        args.raw_output,
    ])
    run_command([
        sys.executable,
        "-m",
        "scripts.audit_logs",
        "--input",
        args.raw_output,
        "--output",
        args.audit_output,
    ])

    ended_at = datetime.now(timezone.utc)
    write_generation_metadata(
        args.metadata,
        {
            "dataset_version": "raw_v1",
            "run_id": run_id,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "base_url": args.base_url,
            "normal_requests": args.normal_requests,
            "fast": args.fast,
            "raw_output": args.raw_output,
            "ground_truth": args.ground_truth,
            "audit_output": args.audit_output,
            "notes": "Normal sessions first, then export/delete/bola anomaly sessions. Simulators only target local StudyDrive.",
        },
    )
    print(f"DONE raw dataset v1: {args.raw_output}, {args.ground_truth}, {args.metadata}")


if __name__ == "__main__":
    main()
