"""Create deterministic local demo data for StudyDrive.

Run from the project root with:
    python -m scripts.seed
"""

from __future__ import annotations

import mimetypes
import uuid
from dataclasses import dataclass
from pathlib import Path

from flask import current_app

from app import create_app
from app.extensions import db
from app.models import FileShare, Folder, StoredFile, User

ADMIN_PASSWORD = "StudyDriveAdmin@2026"
USER_PASSWORD = "StudyDriveUser@2026"


@dataclass(frozen=True)
class DemoAccount:
    username: str
    email: str
    role: str
    password: str


DEMO_ACCOUNTS = (
    DemoAccount("admin", "admin@studydrive.local", "ADMIN", ADMIN_PASSWORD),
    DemoAccount("user1", "user1@studydrive.local", "USER", USER_PASSWORD),
    DemoAccount("user2", "user2@studydrive.local", "USER", USER_PASSWORD),
    DemoAccount("user3", "user3@studydrive.local", "USER", USER_PASSWORD),
    DemoAccount("user4", "user4@studydrive.local", "USER", USER_PASSWORD),
    DemoAccount("user5", "user5@studydrive.local", "USER", USER_PASSWORD),
)

FOLDER_NAMES = ("Bài giảng", "Bài tập", "Tài liệu tham khảo")

FILE_TEMPLATES = {
    "Bài giảng": (
        ("bai-giang-01.txt", "Ghi chú bài giảng số 1"),
        ("bai-giang-02.txt", "Ghi chú bài giảng số 2"),
        ("bai-giang-03.txt", "Ghi chú bài giảng số 3"),
        ("de-cuong-mon-hoc.txt", "Đề cương môn học mẫu"),
        ("lich-hoc.csv", "tuan,noi_dung\n1,Tong quan\n2,Thuc hanh\n"),
    ),
    "Bài tập": (
        ("bai-tap-01.txt", "Bài tập thực hành số 1"),
        ("bai-tap-02.txt", "Bài tập thực hành số 2"),
        ("bai-tap-03.txt", "Bài tập thực hành số 3"),
        ("checklist-bai-tap.txt", "Checklist hoàn thành bài tập"),
        ("ket-qua-bai-tap.csv", "bai,diem\n1,8.5\n2,9.0\n"),
    ),
    "Tài liệu tham khảo": (
        ("tai-lieu-01.txt", "Tài liệu tham khảo số 1"),
        ("tai-lieu-02.txt", "Tài liệu tham khảo số 2"),
        ("tai-lieu-03.txt", "Tài liệu tham khảo số 3"),
        ("lien-ket-tham-khao.txt", "Danh sách liên kết tham khảo mẫu"),
        ("danh-muc-tai-lieu.csv", "stt,ten\n1,Tai lieu A\n2,Tai lieu B\n"),
    ),
}


def _get_or_create_user(account: DemoAccount) -> User:
    user = User.query.filter_by(username=account.username).first()
    if user is None:
        user = User(username=account.username, email=account.email)
        user.set_password(account.password)
        db.session.add(user)
    elif not user.check_password(account.password):
        user.set_password(account.password)

    user.email = account.email
    user.role = account.role
    user.is_active = True
    db.session.flush()
    return user


def _get_or_create_folder(owner: User, name: str) -> Folder:
    folder = Folder.query.filter_by(
        owner_id=owner.id, parent_id=None, name=name
    ).first()
    if folder is None:
        folder = Folder(name=name, owner=owner, parent_id=None)
        db.session.add(folder)
    folder.is_deleted = False
    folder.deleted_at = None
    db.session.flush()
    return folder


def _file_identity(username: str, folder_name: str, original_name: str) -> str:
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"studydrive:{username}:{folder_name}:{original_name}",
        )
    )


def _write_demo_file(path: Path, username: str, folder_name: str, body: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "Dữ liệu mẫu StudyDrive\n"
        f"Owner: {username}\n"
        f"Folder: {folder_name}\n\n"
        f"{body}\n"
    )
    path.write_text(content, encoding="utf-8", newline="\n")
    return path.stat().st_size


def _get_or_create_file(
    owner: User,
    folder: Folder,
    original_name: str,
    body: str,
) -> StoredFile:
    extension = Path(original_name).suffix.lower().lstrip(".")
    uuid_name = _file_identity(owner.username, folder.name, original_name)
    stored_name = f"{uuid_name}.{extension}"
    relative_path = Path("uploads") / owner.username / stored_name
    physical_path = Path(current_app.instance_path) / relative_path
    actual_size = _write_demo_file(physical_path, owner.username, folder.name, body)
    mime_type = mimetypes.guess_type(original_name)[0] or "application/octet-stream"

    stored_file = StoredFile.query.filter_by(stored_name=stored_name).first()
    if stored_file is None:
        stored_file = StoredFile(stored_name=stored_name)
        db.session.add(stored_file)

    stored_file.original_name = original_name
    stored_file.storage_path = relative_path.as_posix()
    stored_file.mime_type = mime_type
    stored_file.file_extension = extension
    stored_file.file_size = actual_size
    stored_file.owner = owner
    stored_file.folder = folder
    stored_file.is_deleted = False
    stored_file.deleted_at = None
    db.session.flush()
    return stored_file


def _seed_sample_shares(users: dict[str, User], files: dict[str, list[StoredFile]]) -> None:
    """Create one deterministic VIEWER share for each normal user."""
    usernames = [f"user{i}" for i in range(1, 6)]
    for index, owner_name in enumerate(usernames):
        recipient_name = usernames[(index + 1) % len(usernames)]
        file_to_share = files[owner_name][0]
        owner = users[owner_name]
        recipient = users[recipient_name]

        share = FileShare.query.filter_by(
            file_id=file_to_share.id,
            shared_with_user_id=recipient.id,
        ).first()
        if share is None:
            share = FileShare(
                file=file_to_share,
                shared_with_user=recipient,
                shared_by_user=owner,
            )
            db.session.add(share)
        share.permission = "VIEWER"
        share.revoked_at = None


def seed_demo_data() -> dict[str, int]:
    """Create or repair the fixed demo dataset without duplicating rows."""
    users: dict[str, User] = {}
    files_by_user: dict[str, list[StoredFile]] = {}

    for account in DEMO_ACCOUNTS:
        users[account.username] = _get_or_create_user(account)

    for username in [f"user{i}" for i in range(1, 6)]:
        owner = users[username]
        files_by_user[username] = []
        for folder_name in FOLDER_NAMES:
            folder = _get_or_create_folder(owner, folder_name)
            for original_name, body in FILE_TEMPLATES[folder_name]:
                files_by_user[username].append(
                    _get_or_create_file(owner, folder, original_name, body)
                )

    _seed_sample_shares(users, files_by_user)
    db.session.commit()

    return {
        "users": User.query.count(),
        "folders": Folder.query.count(),
        "files": StoredFile.query.count(),
        "shares": FileShare.query.count(),
    }


def main() -> None:
    app = create_app()
    with app.app_context():
        from app import models  # noqa: F401

        db.create_all()
        try:
            counts = seed_demo_data()
        except Exception:
            db.session.rollback()
            raise

        print(
            "Seed hoàn tất: "
            f"{counts['users']} users, "
            f"{counts['folders']} folders, "
            f"{counts['files']} files, "
            f"{counts['shares']} shares."
        )


if __name__ == "__main__":
    main()
