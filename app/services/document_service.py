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
from app.models import Folder, StoredFile, User


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
