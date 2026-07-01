"""Run web-integrated detection from the command line.

Examples:
    python -m scripts.run_detection
    python -m scripts.run_detection --start 2026-07-01T00:00:00 --end 2026-07-02T00:00:00
"""

from __future__ import annotations

import argparse
from datetime import datetime

from app import create_app
from app.services.detection_service import run_detection


def parse_datetime(raw: str | None):
    if not raw:
        return None
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Run detection and persist Alert rows.")
    parser.add_argument("--config", default="development")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--model", default="artifacts/models/iforest_v1/model.joblib")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    app = create_app(args.config)
    with app.app_context():
        result = run_detection(start=parse_datetime(args.start), end=parse_datetime(args.end), limit=args.limit, model_path=args.model)
        print(result)
        if not result.ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
