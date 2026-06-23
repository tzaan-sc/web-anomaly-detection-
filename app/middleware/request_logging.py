"""Structured request logging middleware for StudyDrive."""

from __future__ import annotations

import time
import uuid

from flask import Flask, g
from werkzeug.wrappers import Response

from app.services.log_service import save_request_log


def register_request_logging(app: Flask) -> None:
    """Register before/after hooks that log every handled request safely."""

    @app.before_request
    def start_request_timer() -> None:
        # UUID is random and safe to expose for debugging/correlation.
        g.request_id = uuid.uuid4().hex
        g.request_start_time = time.perf_counter()

    @app.after_request
    def write_structured_request_log(response: Response) -> Response:
        started_at = g.get("request_start_time")
        if started_at is None:
            response_time_ms = 0.0
        else:
            response_time_ms = (time.perf_counter() - started_at) * 1000

        request_id = g.get("request_id")
        if request_id:
            response.headers["X-Request-ID"] = request_id

        try:
            save_request_log(response, response_time_ms)
        except Exception:
            # Logging must never make the main web request fail.
            app.logger.exception("Không thể ghi RequestLog cho request_id=%s", request_id)

        return response
