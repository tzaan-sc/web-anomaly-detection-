"""Business logic for safe folder creation, upload, and file browsing."""

from __future__ import annotations

import mimetypes
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from flask import current_app
from sqlalchemy import func
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import FileShare, Folder, StoredFile, User


class DocumentValidationError(ValueError):
    """Raised when user-provided document data is invalid."""


# The browser-provided MIME type is not trusted by itself.  We require an
# allowed extension, an extension/MIME pairing, and a basic signature check for
# formats with a reliable magic number.
MIME_TYPES_BY_EXTENSION: dict[str, set[str]] = {
    "pdf": {"application/pdf"},
    "doc": {
        "application/msword",
        "application/octet-stream",
        "application/x-ole-storage",
    },
    "docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
        "application/octet-stream",
    },
    "xls": {
        "application/vnd.ms-excel",
        "application/octet-stream",
        "application/x-ole-storage",
    },
    "xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
        "application/octet-stream",
    },
    "ppt": {
        "application/vnd.ms-powerpoint",
        "application/octet-stream",
        "application/x-ole-storage",
    },
    "pptx": {
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/zip",
        "application/octet-stream",
    },
    "txt": {"text/plain", "application/octet-stream"},
    "csv": {
        "text/csv",
        "application/csv",
        "text/plain",
        "application/vnd.ms-excel",
        "application/octet-stream",
    },
    "png": {"image/png"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "zip": {
        "application/zip",
        "application/x-zip-compressed",
        "multipart/x-zip",
        "application/octet-stream",
    },
}


@dataclass(frozen=True)
class PreparedUpload:
    original_name: str
    extension: str
    mime_type: str
    stored_name: str


def _basename_from_client_name(filename: str) -> str:
    """Discard every client path component, including Windows separators."""
    normalized = filename.replace("\\", "/")
    return PurePosixPath(normalized).name


def _read_header(file_storage: FileStorage, size: int = 8192) -> bytes:
    position = file_storage.stream.tell()
    header = file_storage.stream.read(size)
    file_storage.stream.seek(position)
    return header


def _signature_matches(extension: str, header: bytes) -> bool:
    """Perform lightweight server-side signature checks where dependable."""
    if extension == "pdf":
        return header.startswith(b"%PDF-")
    if extension == "png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if extension in {"jpg", "jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if extension in {"zip", "docx", "xlsx", "pptx"}:
        return header.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))
    if extension in {"doc", "xls", "ppt"}:
        # Legacy Office files normally use the OLE Compound File signature.
        # Some local tools still upload them as octet-stream, so only reject
        # an explicit non-empty file whose signature is clearly incompatible.
        return header.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")
    if extension in {"txt", "csv"}:
        # NUL bytes are a strong signal that the file is not plain text.
        return b"\x00" not in header
    return True


def prepare_upload(file_storage: FileStorage) -> PreparedUpload:
    """Validate client metadata and produce a collision-resistant server name."""
    raw_name = (file_storage.filename or "").strip()
    if not raw_name:
        raise DocumentValidationError("Tệp không có tên hợp lệ.")

    client_basename = _basename_from_client_name(raw_name)
    safe_name = secure_filename(client_basename)
    extension = Path(client_basename).suffix.lower().lstrip(".")

    allowed_extensions = {
        value.lower() for value in current_app.config.get("ALLOWED_EXTENSIONS", set())
    }
    if not extension or extension not in allowed_extensions:
        raise DocumentValidationError(
            "Định dạng tệp không được phép. Chỉ chấp nhận: "
            + ", ".join(sorted(allowed_extensions))
            + "."
        )

    # secure_filename may return an empty stem for names containing only
    # non-ASCII symbols.  Use a safe fallback while preserving the extension.
    if not safe_name or safe_name in {".", ".."}:
        safe_name = f"file-{uuid.uuid4().hex[:8]}.{extension}"
    elif not safe_name.lower().endswith(f".{extension}"):
        safe_name = f"{Path(safe_name).stem}.{extension}"

    mime_type = (file_storage.mimetype or "application/octet-stream")
    mime_type = mime_type.split(";", 1)[0].strip().lower()
    allowed_mimes = MIME_TYPES_BY_EXTENSION.get(extension, set())
    if allowed_mimes and mime_type not in allowed_mimes:
        guessed_mime = mimetypes.guess_type(safe_name)[0] or "unknown"
        raise DocumentValidationError(
            f"MIME type '{mime_type}' không phù hợp với .{extension} "
            f"(dự kiến {guessed_mime})."
        )

    header = _read_header(file_storage)
    if not header:
        raise DocumentValidationError("Không được upload tệp rỗng.")
    if not _signature_matches(extension, header):
        raise DocumentValidationError(
            f"Nội dung tệp không khớp với định dạng .{extension}."
        )

    stored_name = f"{uuid.uuid4().hex}.{extension}"
    return PreparedUpload(
        original_name=safe_name,
        extension=extension,
        mime_type=mime_type,
        stored_name=stored_name,
    )


def get_owned_folder(folder_id: int | None, owner_id: int) -> Folder | None:
    """Return an active folder only when it belongs to the current owner."""
    if not folder_id:
        return None
    return Folder.query.filter_by(
        id=folder_id,
        owner_id=owner_id,
        is_deleted=False,
    ).first()


def create_folder(*, owner: User, name: str, parent: Folder | None) -> Folder:
    clean_name = name.strip()
    if clean_name in {".", ".."}:
        raise DocumentValidationError("Tên thư mục không hợp lệ.")
    if "/" in clean_name or "\\" in clean_name:
        raise DocumentValidationError("Tên thư mục không được chứa dấu / hoặc \\.")
    if parent is not None and parent.owner_id != owner.id:
        raise DocumentValidationError("Bạn không có quyền tạo thư mục tại vị trí này.")

    duplicate = Folder.query.filter(
        Folder.owner_id == owner.id,
        Folder.parent_id == (parent.id if parent else None),
        Folder.is_deleted.is_(False),
        func.lower(Folder.name) == clean_name.lower(),
    ).first()
    if duplicate is not None:
        raise DocumentValidationError("Đã có thư mục cùng tên tại vị trí này.")

    folder = Folder(name=clean_name, owner=owner, parent=parent)
    db.session.add(folder)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return folder


def save_uploaded_file(
    *,
    file_storage: FileStorage,
    owner: User,
    folder: Folder | None,
) -> StoredFile:
    """Save physical bytes and metadata atomically as far as local FS permits.

    The physical file is written first.  If database persistence fails, the
    session is rolled back and the just-written file is removed.
    """
    if folder is not None and folder.owner_id != owner.id:
        raise DocumentValidationError("Bạn không có quyền upload vào thư mục này.")

    prepared = prepare_upload(file_storage)
    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    owner_directory = (upload_root / str(owner.id)).resolve()

    # Defense in depth: the computed directory must stay under UPLOAD_FOLDER.
    try:
        owner_directory.relative_to(upload_root)
    except ValueError as exc:
        raise DocumentValidationError("Đường dẫn lưu trữ không hợp lệ.") from exc

    owner_directory.mkdir(parents=True, exist_ok=True)
    physical_path = owner_directory / prepared.stored_name
    while physical_path.exists():
        prepared = PreparedUpload(
            original_name=prepared.original_name,
            extension=prepared.extension,
            mime_type=prepared.mime_type,
            stored_name=f"{uuid.uuid4().hex}.{prepared.extension}",
        )
        physical_path = owner_directory / prepared.stored_name

    saved = False
    try:
        file_storage.stream.seek(0)
        file_storage.save(physical_path)
        saved = True

        actual_size = physical_path.stat().st_size
        max_size = int(current_app.config.get("MAX_CONTENT_LENGTH", 20 * 1024 * 1024))
        if actual_size <= 0:
            raise DocumentValidationError("Không được upload tệp rỗng.")
        if actual_size > max_size:
            raise DocumentValidationError("Tệp vượt quá giới hạn 20 MB.")

        instance_root = Path(current_app.instance_path).resolve()
        try:
            storage_path = physical_path.relative_to(instance_root).as_posix()
        except ValueError:
            # UPLOAD_FOLDER may be customized outside instance in deployment.
            storage_path = physical_path.as_posix()

        stored_file = StoredFile(
            original_name=prepared.original_name,
            stored_name=prepared.stored_name,
            storage_path=storage_path,
            mime_type=prepared.mime_type,
            file_extension=prepared.extension,
            file_size=actual_size,
            owner=owner,
            folder=folder,
            is_deleted=False,
        )
        db.session.add(stored_file)
        db.session.commit()
        return stored_file
    except Exception:
        db.session.rollback()
        if saved:
            physical_path.unlink(missing_ok=True)
        raise


def active_folder_choices(owner_id: int) -> list[tuple[int, str]]:
    """Return hierarchical select choices without exposing another user."""
    folders = Folder.query.filter_by(owner_id=owner_id, is_deleted=False).all()
    by_parent: dict[int | None, list[Folder]] = {}
    for folder in folders:
        by_parent.setdefault(folder.parent_id, []).append(folder)
    for children in by_parent.values():
        children.sort(key=lambda item: item.name.casefold())

    choices: list[tuple[int, str]] = [(0, "My Drive (thư mục gốc)")]
    visited: set[int] = set()

    def walk(parent_id: int | None, depth: int) -> None:
        for folder in by_parent.get(parent_id, []):
            if folder.id in visited:
                continue
            visited.add(folder.id)
            choices.append((folder.id, f"{'— ' * depth}{folder.name}"))
            walk(folder.id, depth + 1)

    walk(None, 0)
    return choices


def folder_breadcrumb(folder: Folder | None) -> list[Folder]:
    """Build root-to-current ancestry and stop safely if data is cyclic."""
    if folder is None:
        return []
    chain: list[Folder] = []
    seen: set[int] = set()
    current: Folder | None = folder
    while current is not None and current.id not in seen:
        seen.add(current.id)
        chain.append(current)
        current = current.parent
    chain.reverse()
    return chain


def format_file_size(size: int) -> str:
    value = float(size or 0)
    units = ("B", "KB", "MB", "GB")
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


# Object-level authorization -------------------------------------------------

ACCESS_OWNER = "OWNER"
ACCESS_VIEWER = "VIEWER"
ACCESS_NONE = "NONE"


def get_file_access(stored_file: StoredFile | None, user_id: int) -> str:
    """Return OWNER, VIEWER, or NONE for one active file.

    Deleted files are deliberately treated as inaccessible.  This keeps the
    same rule in HTML routes, download routes, API routes, and future
    simulators used to generate IDOR/BOLA traffic.
    """
    if stored_file is None or stored_file.is_deleted:
        return ACCESS_NONE
    if stored_file.owner_id == user_id:
        return ACCESS_OWNER

    active_share = FileShare.query.filter_by(
        file_id=stored_file.id,
        shared_with_user_id=user_id,
        permission=ACCESS_VIEWER,
        revoked_at=None,
    ).first()
    return ACCESS_VIEWER if active_share is not None else ACCESS_NONE


def can_view_file(stored_file: StoredFile | None, user_id: int) -> bool:
    """True only for OWNER or an active VIEWER share."""
    return get_file_access(stored_file, user_id) in {ACCESS_OWNER, ACCESS_VIEWER}


def can_modify_file(stored_file: StoredFile | None, user_id: int) -> bool:
    """True only for the active file owner."""
    return get_file_access(stored_file, user_id) == ACCESS_OWNER


def resolve_physical_file(stored_file: StoredFile) -> Path:
    """Resolve a server-controlled storage path and reject unsafe metadata.

    The client supplies only ``file_id``.  The path always comes from database
    metadata and must still remain under the configured upload directory.
    """
    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    stored_path = Path(stored_file.storage_path)
    physical_path = (
        stored_path.resolve()
        if stored_path.is_absolute()
        else (Path(current_app.instance_path) / stored_path).resolve()
    )

    try:
        physical_path.relative_to(upload_root)
    except ValueError as exc:
        raise FileNotFoundError("Unsafe stored file path") from exc

    # Defense in depth against corrupted or manually edited metadata.
    if physical_path.name != stored_file.stored_name:
        raise FileNotFoundError("Stored filename does not match metadata")
    if not physical_path.is_file():
        raise FileNotFoundError("Physical file is missing")
    return physical_path


def _validate_display_name(stored_file: StoredFile, new_name: str) -> str:
    clean_name = (new_name or "").strip()
    if not clean_name or clean_name in {".", ".."}:
        raise DocumentValidationError("Tên tệp không hợp lệ.")
    if len(clean_name) > 255:
        raise DocumentValidationError("Tên tệp tối đa 255 ký tự.")
    if "/" in clean_name or "\\" in clean_name:
        raise DocumentValidationError("Tên tệp không được chứa dấu / hoặc \\.")

    extension = Path(clean_name).suffix.lower().lstrip(".")
    if extension != stored_file.file_extension.lower():
        raise DocumentValidationError(
            f"Tên mới phải giữ nguyên phần mở rộng .{stored_file.file_extension}."
        )
    return clean_name


def rename_file(*, stored_file: StoredFile, owner: User, new_name: str) -> StoredFile:
    """Rename display metadata only; never change UUID-backed storage fields."""
    if not can_modify_file(stored_file, owner.id):
        raise PermissionError("Only the owner may rename this file")

    clean_name = _validate_display_name(stored_file, new_name)
    duplicate = StoredFile.query.filter(
        StoredFile.id != stored_file.id,
        StoredFile.owner_id == owner.id,
        StoredFile.folder_id == stored_file.folder_id,
        StoredFile.is_deleted.is_(False),
        func.lower(StoredFile.original_name) == clean_name.lower(),
    ).first()
    if duplicate is not None:
        raise DocumentValidationError("Đã có tệp cùng tên tại vị trí này.")

    stored_file.original_name = clean_name
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return stored_file


def move_file(
    *, stored_file: StoredFile, owner: User, target_folder: Folder | None
) -> StoredFile:
    """Move an owned file to root or another active folder of the same owner."""
    if not can_modify_file(stored_file, owner.id):
        raise PermissionError("Only the owner may move this file")
    if target_folder is not None and (
        target_folder.owner_id != owner.id or target_folder.is_deleted
    ):
        raise DocumentValidationError("Bạn không có quyền di chuyển vào thư mục này.")

    target_folder_id = target_folder.id if target_folder else None
    duplicate = StoredFile.query.filter(
        StoredFile.id != stored_file.id,
        StoredFile.owner_id == owner.id,
        StoredFile.folder_id == target_folder_id,
        StoredFile.is_deleted.is_(False),
        func.lower(StoredFile.original_name) == stored_file.original_name.lower(),
    ).first()
    if duplicate is not None:
        raise DocumentValidationError("Thư mục đích đã có tệp cùng tên.")

    stored_file.folder = target_folder
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return stored_file


def share_file(
    *, stored_file: StoredFile, owner: User, recipient: User
) -> FileShare:
    """Grant or restore the single supported permission: VIEWER."""
    if not can_modify_file(stored_file, owner.id):
        raise PermissionError("Only the owner may share this file")
    if recipient.id == owner.id:
        raise DocumentValidationError("Không thể chia sẻ tệp cho chính chủ sở hữu.")
    if not recipient.is_active or recipient.role.upper() != "USER":
        raise DocumentValidationError("Người nhận không hợp lệ hoặc đã bị khóa.")

    existing = FileShare.query.filter_by(
        file_id=stored_file.id,
        shared_with_user_id=recipient.id,
    ).first()
    if existing is not None and existing.revoked_at is None:
        raise DocumentValidationError("Tệp đã được chia sẻ cho người dùng này.")

    if existing is None:
        existing = FileShare(
            file=stored_file,
            shared_with_user=recipient,
            shared_by_user=owner,
            permission=ACCESS_VIEWER,
        )
        db.session.add(existing)
    else:
        existing.permission = ACCESS_VIEWER
        existing.shared_by_user = owner
        existing.revoked_at = None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return existing


def revoke_file_share(
    *, stored_file: StoredFile, owner: User, share: FileShare
) -> FileShare:
    """Revoke access immediately while retaining the audit-friendly row."""
    if not can_modify_file(stored_file, owner.id):
        raise PermissionError("Only the owner may revoke a share")
    if share.file_id != stored_file.id or share.revoked_at is not None:
        raise DocumentValidationError("Lượt chia sẻ không còn hiệu lực.")

    from datetime import datetime, timezone

    share.revoked_at = datetime.now(timezone.utc)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return share


def share_recipient_choices(owner_id: int) -> list[tuple[int, str]]:
    """Return active normal users except the owner; IDs are rechecked on POST."""
    users = (
        User.query.filter(
            User.id != owner_id,
            User.is_active.is_(True),
            func.upper(User.role) == "USER",
        )
        .order_by(func.lower(User.username).asc())
        .all()
    )
    return [(user.id, f"{user.username} ({user.email})") for user in users]

# Soft delete / trash ---------------------------------------------------------


def soft_delete_file(*, stored_file: StoredFile | None, owner: User) -> StoredFile:
    """Move an owned active file to trash without deleting physical bytes."""
    if stored_file is None or stored_file.owner_id != owner.id:
        raise PermissionError("Only the owner may delete this file")
    if stored_file.is_deleted:
        return stored_file

    from datetime import datetime, timezone

    stored_file.is_deleted = True
    stored_file.deleted_at = datetime.now(timezone.utc)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return stored_file


def restore_file(*, stored_file: StoredFile | None, owner: User) -> StoredFile:
    """Restore an owned file from trash."""
    if stored_file is None or stored_file.owner_id != owner.id:
        raise PermissionError("Only the owner may restore this file")
    if not stored_file.is_deleted:
        return stored_file

    stored_file.is_deleted = False
    stored_file.deleted_at = None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return stored_file


def permanently_delete_file(*, stored_file: StoredFile | None, owner: User) -> None:
    """Permanently remove an owned trashed file and then try to delete bytes."""
    if stored_file is None or stored_file.owner_id != owner.id:
        raise PermissionError("Only the owner may permanently delete this file")
    if not stored_file.is_deleted:
        raise DocumentValidationError("Chỉ được xóa vĩnh viễn tệp đang ở thùng rác.")

    physical_path: Path | None = None
    try:
        physical_path = resolve_physical_file(stored_file)
    except FileNotFoundError:
        physical_path = None

    try:
        db.session.delete(stored_file)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    if physical_path is not None:
        physical_path.unlink(missing_ok=True)
