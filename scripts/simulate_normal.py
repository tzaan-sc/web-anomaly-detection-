"""Generate normal StudyDrive behavior with varied user/session profiles."""

from __future__ import annotations

import argparse
import io
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
    now_iso,
    post_with_csrf,
    request_with_timeout,
    sleep_random,
)

PROFILE_WEIGHTS = {
    "casual": {
        "list": 35,
        "search": 18,
        "detail": 20,
        "download": 15,
        "folder": 6,
        "shared": 3,
        "upload": 2,
        "rename": 1,
        "export": 0.5,
        "delete": 0.2,
    },
    "active": {
        "list": 24,
        "search": 15,
        "detail": 24,
        "download": 18,
        "folder": 8,
        "shared": 4,
        "upload": 3,
        "rename": 2,
        "export": 1,
        "delete": 0.3,
    },
    "reviewer": {
        "list": 18,
        "search": 10,
        "detail": 28,
        "download": 28,
        "folder": 4,
        "shared": 8,
        "upload": 1,
        "rename": 1,
        "export": 0.5,
        "delete": 0.1,
    },
}

SEARCH_TERMS = ["bao", "hoc", "slide", "report", "demo", "txt", "pdf", "data"]


def weighted_action(profile: str) -> str:
    weights = PROFILE_WEIGHTS[profile]
    actions = list(weights)
    return random.choices(actions, weights=[weights[action] for action in actions], k=1)[0]


def run_action(session: requests.Session, base_url: str, user_data, action: str, request_index: int) -> int:
    owned_id = choose_file_id(user_data.owned_file_ids)
    visible_id = choose_file_id(user_data.owned_file_ids + user_data.shared_file_ids)

    if action == "list":
        request_with_timeout(session, "GET", f"{base_url}/files")
        return 1
    if action == "search":
        q = random.choice(SEARCH_TERMS)
        request_with_timeout(session, "GET", f"{base_url}/files", params={"q": q, "sort": random.choice(["newest", "name_asc", "size_desc"])})
        return 1
    if action == "folder" and user_data.folder_ids:
        folder_id = random.choice(user_data.folder_ids)
        request_with_timeout(session, "GET", f"{base_url}/folders/{folder_id}")
        return 1
    if action == "shared":
        request_with_timeout(session, "GET", f"{base_url}/shared-with-me")
        return 1
    if action == "detail" and visible_id:
        request_with_timeout(session, "GET", f"{base_url}/files/{visible_id}")
        return 1
    if action == "download" and visible_id:
        request_with_timeout(session, "GET", f"{base_url}/files/{visible_id}/download")
        return 1
    if action == "upload":
        content = f"normal upload {user_data.username} {request_index} {now_iso()}\n".encode("utf-8")
        files = {"file": (f"normal_{request_index}.txt", io.BytesIO(content), "text/plain")}
        response = post_with_csrf(
            session,
            base_url,
            "/files/upload",
            data={"folder_id": "0"},
            files=files,
        )
        if response.status_code in {302, 200}:
            return 2  # GET form + POST upload
        return 2
    if action == "rename" and owned_id:
        api_response = request_with_timeout(session, "GET", f"{base_url}/api/files/{owned_id}")
        extension = "txt"
        if api_response.status_code == 200:
            extension = api_response.json().get("file_extension") or "txt"
        new_name = f"normal_renamed_{request_index}.{extension}"
        post_with_csrf(
            session,
            base_url,
            f"/files/{owned_id}/rename",
            data={"original_name": new_name},
        )
        return 3
    if action == "export":
        # Normal export is rare and uses current safe filter, not many rapid exports.
        post_with_csrf(
            session,
            base_url,
            "/files",
            post_path="/files/export",
            data={"q": "", "extension": "", "folder": ""},
        )
        return 2
    if action == "delete" and owned_id:
        try:
            post_with_csrf(session, base_url, f"/files/{owned_id}", post_path=f"/files/{owned_id}/delete")
        finally:
            if owned_id in user_data.owned_file_ids:
                user_data.owned_file_ids.remove(owned_id)
        return 2

    request_with_timeout(session, "GET", f"{base_url}/files")
    return 1


def simulate_for_user(args, username: str, profile: str, request_budget: int, run_id: str) -> dict[str, object]:
    user_data = load_demo_user_data(username)
    session = requests.Session()
    session.headers.update({"User-Agent": f"StudyDriveNormalSimulator/{profile}"})
    started_at = datetime.now(timezone.utc)
    login(session, args.base_url, username, args.password)
    request_count = 2  # login GET + POST

    for i in range(request_budget):
        action = weighted_action(profile)
        try:
            request_count += run_action(session, args.base_url, user_data, action, i)
        except Exception as e:
            request_count += 1
            # Quietly log the warning instead of raising to keep the loop going
            print(f"  [Warning] User {username} action {action} failed (ID: {owned_id if 'owned_id' in locals() else 'N/A'}): {e}")
        sleep_random(fast=args.fast)

    ended_at = datetime.now(timezone.utc)
    row = {
        "scenario_id": f"normal:{run_id}:{username}",
        "scenario": "normal",
        "label": 0,
        "run_id": run_id,
        "user_id": user_data.user_id,
        "username": username,
        "session_name": profile,
        "severity": "normal",
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "request_count": request_count,
        "notes": f"profile={profile}; varied normal behavior; no intentional 403 burst",
    }
    append_ground_truth(args.ground_truth, row)
    return row


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Sinh request normal cho StudyDrive local.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--users", default="user1,user2,user3", help="Danh sách username, phân tách bằng dấu phẩy")
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--requests", type=int, default=250, help="Tổng số action normal dự kiến")
    parser.add_argument("--fast", action="store_true", help="Delay rất ngắn để sinh dataset nhanh")
    parser.add_argument("--seed", type=int, default=20260626)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--ground-truth", default="data/raw/ground_truth.csv")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    random.seed(args.seed)
    run_id = args.run_id or make_run_id("normal")
    users = [item.strip() for item in args.users.split(",") if item.strip()]
    profiles = list(PROFILE_WEIGHTS)
    per_user = max(args.requests // max(len(users), 1), 1)

    print(f"Run normal: run_id={run_id}, users={users}, per_user_actions={per_user}")
    rows = []
    for index, username in enumerate(users):
        profile = profiles[index % len(profiles)]
        rows.append(simulate_for_user(args, username, profile, per_user, run_id))
        print(f"  OK {username} profile={profile}")
    print(f"Đã ghi ground truth cho {len(rows)} normal session -> {args.ground_truth}")


if __name__ == "__main__":
    main()
