"""Small orchestrator for week 6 demo commands.

Run this while Flask server is running in another terminal:
    python run.py

Examples:
    python -m scripts.run_demo_scenario --scenario export --fast
    python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 800
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import requests

from scripts.simulator_common import DEFAULT_BASE_URL, make_run_id


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def assert_server(base_url: str) -> None:
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
    except Exception as exc:
        raise SystemExit("Server chưa chạy. Mở terminal khác và chạy `python run.py` trước.") from exc


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Run one/all demo scenario(s) then detection.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--scenario", choices=["normal", "export", "delete", "bola", "all"], default="all")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--skip-reset", action="store_true")
    parser.add_argument("--normal-requests", type=int, default=800)
    parser.add_argument("--ground-truth", default="data/raw/ground_truth.csv")
    parser.add_argument("--raw-output", default="data/raw/request_logs_raw.csv")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    assert_server(args.base_url)
    run_id = make_run_id(f"demo_{args.scenario}")
    fast = ["--fast"] if args.fast else []

    if not args.skip_reset:
        run([sys.executable, "-m", "scripts.reset_demo"])
        gt = Path(args.ground_truth)
        if gt.exists():
            gt.unlink()

    if args.scenario in {"normal", "all"}:
        run([
            sys.executable, "-m", "scripts.simulate_normal", "--base-url", args.base_url,
            "--users", "user1,user2,user3,user4,user5", "--requests", str(args.normal_requests),
            "--run-id", run_id, "--ground-truth", args.ground_truth, *fast,
        ])
    if args.scenario in {"export", "all"}:
        for severity, username in [("mild", "user1"), ("medium", "user2"), ("high", "user3")]:
            run([
                sys.executable, "-m", "scripts.simulate_export_abuse", "--base-url", args.base_url,
                "--username", username, "--severity", severity, "--run-id", run_id,
                "--ground-truth", args.ground_truth, *fast,
            ])
    if args.scenario in {"delete", "all"}:
        for severity, username in [("mild", "user4"), ("medium", "user5")]:
            run([
                sys.executable, "-m", "scripts.simulate_delete_abuse", "--base-url", args.base_url,
                "--username", username, "--severity", severity, "--run-id", run_id,
                "--ground-truth", args.ground_truth, *fast,
            ])
    if args.scenario in {"bola", "all"}:
        for mode, username in [("low-and-slow", "user1"), ("burst", "user2")]:
            run([
                sys.executable, "-m", "scripts.simulate_bola_scan", "--base-url", args.base_url,
                "--username", username, "--mode", mode, "--run-id", run_id,
                "--ground-truth", args.ground_truth, *fast,
            ])

    run([sys.executable, "-m", "scripts.export_logs", "--output", args.raw_output])
    run([sys.executable, "-m", "ml.build_features", "--logs", args.raw_output, "--ground-truth", args.ground_truth])
    run([sys.executable, "-m", "ml.train", "--tune"])
    run([sys.executable, "-m", "ml.evaluate"])
    run([sys.executable, "-m", "scripts.run_detection"])
    print("DONE demo scenario. Mở /alerts để xem cảnh báo.")


if __name__ == "__main__":
    main()
