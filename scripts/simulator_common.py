"""Shared helpers for local StudyDrive behavior simulators.

All simulators in this project are designed for the owner's local Flask server
only. They do not attack external systems and they only use StudyDrive demo
accounts/data.
"""

from __future__ import annotations

import csv
import json
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests

from app import create_app
from app.models import FileShare, Folder, StoredFile, User

DEFAULT_BASE_URL = "http://127.0.0.1:5000"
DEFAULT_PASSWORD = "StudyDriveUser@2026"
GROUND_TRUTH_COLUMNS = [
    "scenario_id",
    "scenario",
    "label",
    "run_id",
    "user_id",
    "username",
    "session_name",
    "severity",
    "started_at",
    "ended_at",
    "request_count",
    "notes",
]

CSRF_RE = re.compile(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']')


@dataclass(frozen=True)
class DemoUserData:
    user_id: int
    username: str
    owned_file_ids: list[int]
    shared_file_ids: list[int]
    folder_ids: list[int]
    other_file_ids: list[int]
    missing_file_ids: list[int]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_run_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


def sleep_random(*, fast: bool, low: float = 0.2, high: float = 1.2) -> None:
    if fast:
        time.sleep(random.uniform(0.01, 0.05))
    else:
        time.sleep(random.uniform(low, high))


def ensure_parent(path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def append_ground_truth(path: str | Path, row: dict[str, object]) -> None:
    output_path = ensure_parent(path)
    write_header = not output_path.exists() or output_path.stat().st_size == 0
    with output_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=GROUND_TRUTH_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({column: row.get(column, "") for column in GROUND_TRUTH_COLUMNS})


def write_generation_metadata(path: str | Path, metadata: dict[str, object]) -> None:
    output_path = ensure_parent(path)
    output_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def extract_csrf(html: str) -> str:
    match = CSRF_RE.search(html)
    if not match:
        raise RuntimeError("Không tìm thấy csrf_token trong HTML. Kiểm tra form/CSRF config.")
    return match.group(1)


def request_with_timeout(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    kwargs.setdefault("timeout", 10)
    response = session.request(method, url, **kwargs)
    return response


def get_csrf(session: requests.Session, base_url: str, path: str) -> str:
    response = request_with_timeout(session, "GET", f"{base_url}{path}")
    response.raise_for_status()
    return extract_csrf(response.text)


def login(session: requests.Session, base_url: str, username: str, password: str = DEFAULT_PASSWORD) -> None:
    login_page = request_with_timeout(session, "GET", f"{base_url}/auth/login")
    login_page.raise_for_status()
    csrf_token = extract_csrf(login_page.text)
    response = request_with_timeout(
        session,
        "POST",
        f"{base_url}/auth/login",
        data={"identifier": username, "password": password, "csrf_token": csrf_token},
        allow_redirects=True,
    )
    response.raise_for_status()
    if "/auth/login" in response.url and "không hợp lệ" in response.text.lower():
        raise RuntimeError(f"Đăng nhập thất bại cho {username}.")


def post_with_csrf(
    session: requests.Session,
    base_url: str,
    form_path: str,
    post_path: str | None = None,
    data: dict[str, object] | None = None,
    files: dict[str, object] | None = None,
) -> requests.Response:
    csrf_token = get_csrf(session, base_url, form_path)
    payload = dict(data or {})
    payload["csrf_token"] = csrf_token
    return request_with_timeout(
        session,
        "POST",
        f"{base_url}{post_path or form_path}",
        data=payload,
        files=files,
        allow_redirects=False,
    )


def load_demo_user_data(username: str, *, owned_limit: int = 50, other_limit: int = 80) -> DemoUserData:
    app = create_app("development")
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise RuntimeError(f"Không tìm thấy demo user '{username}' trong database.")

        owned_file_ids = [
            row[0]
            for row in StoredFile.query.with_entities(StoredFile.id)
            .filter_by(owner_id=user.id, is_deleted=False)
            .order_by(StoredFile.id.asc())
            .limit(owned_limit)
            .all()
        ]
        shared_file_ids = [
            row[0]
            for row in StoredFile.query.with_entities(StoredFile.id)
            .join(FileShare, FileShare.file_id == StoredFile.id)
            .filter(
                FileShare.shared_with_user_id == user.id,
                FileShare.revoked_at.is_(None),
                StoredFile.is_deleted.is_(False),
            )
            .order_by(StoredFile.id.asc())
            .limit(owned_limit)
            .all()
        ]
        folder_ids = [
            row[0]
            for row in Folder.query.with_entities(Folder.id)
            .filter_by(owner_id=user.id, is_deleted=False)
            .order_by(Folder.id.asc())
            .all()
        ]
        other_file_ids = [
            row[0]
            for row in StoredFile.query.with_entities(StoredFile.id)
            .filter(StoredFile.owner_id != user.id, StoredFile.is_deleted.is_(False))
            .order_by(StoredFile.id.asc())
            .limit(other_limit)
            .all()
        ]
        max_id = StoredFile.query.with_entities(StoredFile.id).order_by(StoredFile.id.desc()).first()
        start_missing = (max_id[0] if max_id else 1000) + 1
        missing_file_ids = list(range(start_missing, start_missing + other_limit))

        return DemoUserData(
            user_id=user.id,
            username=user.username,
            owned_file_ids=owned_file_ids,
            shared_file_ids=shared_file_ids,
            folder_ids=folder_ids,
            other_file_ids=other_file_ids,
            missing_file_ids=missing_file_ids,
        )


def choose_file_id(candidates: Iterable[int]) -> int | None:
    items = list(candidates)
    if not items:
        return None
    return random.choice(items)
