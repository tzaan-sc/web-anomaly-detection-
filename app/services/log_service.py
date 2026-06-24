"""Helpers for structured and semantic request logging.

The service deliberately stores only request metadata. It must never persist
passwords, CSRF values, raw cookies, session tokens, request bodies, uploaded
file contents, or query-string values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import g, request, session
from sqlalchemy.orm import sessionmaker
from werkzeug.wrappers import Response

from app.extensions import db
from app.models import FileShare, Folder, RequestLog, StoredFile, User


MAX_PATH_LENGTH = 1024
MAX_ENDPOINT_LENGTH = 255
MAX_USER_AGENT_LENGTH = 512
MAX_ROLE_LENGTH = 20
MAX_METHOD_LENGTH = 10
MAX_ACTION_LENGTH = 80
MAX_RESOURCE_TYPE_LENGTH = 50
MAX_RESOURCE_ID_LENGTH = 100
MAX_PERMISSION_LENGTH = 20
MAX_AUTH_RESULT_LENGTH = 20
MAX_IP_LENGTH = 45
MAX_SESSION_HASH_LENGTH = 128
MAX_OWNERSHIP_LENGTH = 20


# Endpoints có file_id trong request.view_args. Không parse URL thô để tránh
# regex rải rác và tránh lấy nhầm id từ query string.
FILE_ENDPOINTS = {
    "documents.file_detail",
    "documents.download_file",
    "documents.file_api",
    "documents.rename_file",
    "documents.move_file",
    "documents.share_file",
    "documents.revoke_share",
    "documents.delete_file",
    "documents.restore_file",
    "documents.permanent_delete_file",
}

FOLDER_ENDPOINTS = {
    "documents.browse_folder",
}

# Action chi tiết: giữ lại để admin đọc log dễ hiểu.
ACTION_BY_ENDPOINT = {
    "main.index": "home",
    "main.dashboard": "dashboard",
    "main.health": "health",
    "auth.login": "login",
    "auth.logout": "logout",
    "auth.profile": "profile",
    "auth.change_password": "change_password",
    "documents.legacy_index": "list_files",
    "documents.index": "list_files",
    "documents.browse_folder": "browse_folder",
    "documents.create_folder": "create_folder",
    "documents.upload_file": "upload_file",
    "documents.file_detail": "view_file_detail",
    "documents.download_file": "download_file",
    "documents.file_api": "api_view_file_detail",
    "documents.rename_file": "rename_file",
    "documents.move_file": "move_file",
    "documents.share_file": "share_file",
    "documents.revoke_share": "revoke_share",
    "documents.shared_with_me": "list_shared_files",
    "documents.trash": "list_trash",
    "documents.delete_file": "delete_file",
    "documents.restore_file": "restore_file",
    "documents.permanent_delete_file": "permanent_delete_file",
    "documents.export_files_csv": "export_files_csv",
    "admin.index": "admin_dashboard",
    "admin.users": "admin_list_users",
    "admin.toggle_user_active": "admin_toggle_user",
    "admin.files": "admin_list_files",
    "admin.folders": "admin_list_folders",
    "admin.logs": "admin_list_logs",
    "admin.log_detail": "admin_view_log_detail",
    "admin.logs_export": "admin_export_logs_csv",
    "alerts.index": "admin_list_alerts",
}

# Action type nhóm lớn: dùng cho ML/feature engineering.
ACTION_TYPE_BY_ENDPOINT = {
    "auth.login": "login",
    "auth.logout": "login",
    "main.dashboard": "list",
    "documents.legacy_index": "list",
    "documents.index": "list",
    "documents.browse_folder": "list",
    "documents.shared_with_me": "list",
    "documents.trash": "list",
    "documents.create_folder": "create",
    "documents.upload_file": "create",
    "documents.file_detail": "view_detail",
    "documents.download_file": "view_detail",
    "documents.file_api": "view_detail",
    "documents.rename_file": "edit",
    "documents.move_file": "edit",
    "documents.share_file": "edit",
    "documents.revoke_share": "edit",
    "auth.profile": "edit",
    "auth.change_password": "edit",
    "documents.export_files_csv": "export",
    "documents.delete_file": "delete",
    "documents.permanent_delete_file": "delete",
    "documents.restore_file": "restore",
    "admin.index": "admin",
    "admin.users": "admin",
    "admin.toggle_user_active": "admin",
    "admin.files": "admin",
    "admin.folders": "admin",
    "admin.logs": "admin",
    "admin.log_detail": "admin",
    "admin.logs_export": "admin",
    "alerts.index": "admin",
}

VALID_ACTION_TYPES = {
    "login",
    "list",
    "create",
    "view_detail",
    "edit",
    "export",
    "delete",
    "restore",
    "admin",
    "other",
}


@dataclass(frozen=True)
class ResourceContext:
    owner_id: int | None = None
    permission: str | None = None
    ownership_result: str | None = None
    file_size: int | None = None


def _truncate(value: Any, max_length: int) -> str | None:
    """Return a string safely truncated for the database column."""
    if value is None:
        return None
    text = str(value)
    if not text:
        return None
    return text[:max_length]


def resolve_action(endpoint: str | None, method: str) -> str:
    """Map a Flask endpoint to a detailed action for humans/admin screens."""
    if endpoint in ACTION_BY_ENDPOINT:
        return ACTION_BY_ENDPOINT[endpoint]
    if endpoint and endpoint.startswith(("admin.", "alerts.")):
        return "admin"
    if method == "POST":
        return "write"
    return "other"


def resolve_action_type(endpoint: str | None, method: str) -> str:
    """Map a Flask endpoint to a stable ML action_type bucket."""
    if endpoint in ACTION_TYPE_BY_ENDPOINT:
        return ACTION_TYPE_BY_ENDPOINT[endpoint]
    if endpoint and endpoint.startswith(("admin.", "alerts.")):
        return "admin"
    if method == "POST":
        return "edit"
    return "other"


def resolve_resource(endpoint: str | None, view_args: dict[str, Any] | None) -> tuple[str | None, str | None]:
    """Extract resource type/id from Flask view_args, not from raw URL text."""
    view_args = view_args or {}

    if endpoint in FILE_ENDPOINTS and "file_id" in view_args:
        return "file", str(view_args["file_id"])

    if endpoint in FOLDER_ENDPOINTS and "folder_id" in view_args:
        return "folder", str(view_args["folder_id"])

    if endpoint == "documents.create_folder" and "parent_id" in view_args:
        return "folder", str(view_args["parent_id"])

    if endpoint == "admin.toggle_user_active" and "user_id" in view_args:
        return "user", str(view_args["user_id"])

    if endpoint == "documents.revoke_share" and "share_id" in view_args:
        return "share", str(view_args["share_id"])

    return None, None


def resolve_authorization_result(status_code: int) -> str:
    """Convert response status code to a coarse authorization/logging result."""
    if status_code in {401, 403, 404}:
        return "denied"
    if 200 <= status_code < 400:
        return "allowed"
    return "error"


def _active_file_share_exists(file_id: int, user_id: int) -> bool:
    return (
        FileShare.query.filter_by(
            file_id=file_id,
            shared_with_user_id=user_id,
            permission="VIEWER",
            revoked_at=None,
        ).first()
        is not None
    )


def resolve_resource_context(
    *,
    resource_type: str | None,
    resource_id: str | None,
    user_id: int | None,
    role: str | None,
) -> ResourceContext:
    """Resolve ownership/permission context without exposing private data.

    The result intentionally stores coarse labels only: OWNER, VIEWER, NONE,
    NOT_FOUND, ADMIN, ANONYMOUS, or UNKNOWN. It does not store filenames,
    storage paths, raw cookies, request bodies, or file contents.
    """
    if role and role.upper() == "ADMIN":
        return ResourceContext(permission="ADMIN", ownership_result="ADMIN")

    if user_id is None:
        return ResourceContext(permission="ANONYMOUS", ownership_result="ANONYMOUS")

    if not resource_type or not resource_id:
        return ResourceContext(permission=None, ownership_result=None)

    try:
        numeric_id = int(resource_id)
    except (TypeError, ValueError):
        return ResourceContext(permission=None, ownership_result="UNKNOWN")

    try:
        if resource_type == "file":
            stored_file = db.session.get(StoredFile, numeric_id)
            if stored_file is None:
                return ResourceContext(permission="NONE", ownership_result="NOT_FOUND")
            if stored_file.owner_id == user_id:
                return ResourceContext(
                    owner_id=stored_file.owner_id,
                    permission="OWNER",
                    ownership_result="OWNER",
                    file_size=stored_file.file_size,
                )
            if not stored_file.is_deleted and _active_file_share_exists(stored_file.id, user_id):
                return ResourceContext(
                    owner_id=stored_file.owner_id,
                    permission="VIEWER",
                    ownership_result="VIEWER",
                    file_size=stored_file.file_size,
                )
            return ResourceContext(
                owner_id=stored_file.owner_id,
                permission="NONE",
                ownership_result="NONE",
                file_size=stored_file.file_size,
            )

        if resource_type == "folder":
            folder = db.session.get(Folder, numeric_id)
            if folder is None:
                return ResourceContext(permission="NONE", ownership_result="NOT_FOUND")
            permission = "OWNER" if folder.owner_id == user_id else "NONE"
            return ResourceContext(
                owner_id=folder.owner_id,
                permission=permission,
                ownership_result=permission,
            )

        if resource_type == "user":
            user = db.session.get(User, numeric_id)
            if user is None:
                return ResourceContext(permission="NONE", ownership_result="NOT_FOUND")
            permission = "SELF" if user.id == user_id else "OTHER_USER"
            return ResourceContext(owner_id=user.id, permission=permission, ownership_result=permission)

        if resource_type == "share":
            share = db.session.get(FileShare, numeric_id)
            if share is None:
                return ResourceContext(permission="NONE", ownership_result="NOT_FOUND")
            stored_file = db.session.get(StoredFile, share.file_id)
            owner_id = stored_file.owner_id if stored_file is not None else None
            permission = "OWNER" if owner_id == user_id else "NONE"
            return ResourceContext(owner_id=owner_id, permission=permission, ownership_result=permission)
    except Exception:
        # A context lookup failure should not prevent the base request log.
        return ResourceContext(permission=None, ownership_result="UNKNOWN")

    return ResourceContext(permission=None, ownership_result=None)


def is_sensitive_request(
    *,
    endpoint: str | None,
    action_type: str,
    authorization_result: str,
    ownership_result: str | None,
) -> bool:
    """Mark requests that are important for security/ML review."""
    if action_type in {"export", "delete", "restore", "admin"}:
        return True
    if endpoint and endpoint.startswith(("admin.", "alerts.")):
        return True
    # Detail/download/API request bị từ chối hoặc không có quyền là tín hiệu IDOR/BOLA.
    if action_type == "view_detail" and (
        authorization_result == "denied" or ownership_result in {"NONE", "NOT_FOUND", "ANONYMOUS"}
    ):
        return True
    return False


def get_client_ip() -> str | None:
    """Return client IP without storing cookies or request body."""
    # In local development this is usually 127.0.0.1. Behind a proxy,
    # access_route gives the forwarded client chain; keep only the first value.
    if request.access_route:
        return _truncate(request.access_route[0], MAX_IP_LENGTH)
    return _truncate(request.remote_addr, MAX_IP_LENGTH)


def build_request_log(response: Response, response_time_ms: float) -> RequestLog:
    """Build a RequestLog row from safe metadata only."""
    endpoint = request.endpoint
    method = request.method.upper()
    action = resolve_action(endpoint, method)
    action_type = resolve_action_type(endpoint, method)
    if action_type not in VALID_ACTION_TYPES:
        action_type = "other"

    resource_type, resource_id = resolve_resource(endpoint, request.view_args)

    current_user = g.get("current_user")
    session_user_id = session.get("user_id")
    session_role = session.get("role")

    user_id = getattr(current_user, "id", None) or session_user_id
    role = getattr(current_user, "role", None) or session_role
    is_authenticated = user_id is not None

    session_id_hash = session.get("session_id_hash")
    authorization_result = resolve_authorization_result(response.status_code)
    context = resolve_resource_context(
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        role=role,
    )
    is_sensitive = is_sensitive_request(
        endpoint=endpoint,
        action_type=action_type,
        authorization_result=authorization_result,
        ownership_result=context.ownership_result,
    )

    # Do not touch request.form, request.get_json(), request.data, cookies,
    # uploaded file streams, CSRF tokens, or passwords here.
    return RequestLog(
        request_id=_truncate(g.get("request_id"), 64),
        user_id=user_id,
        is_authenticated=bool(is_authenticated),
        role=_truncate(role, MAX_ROLE_LENGTH),
        session_id_hash=_truncate(session_id_hash, MAX_SESSION_HASH_LENGTH),
        ip_address=get_client_ip(),
        user_agent=_truncate(request.headers.get("User-Agent"), MAX_USER_AGENT_LENGTH),
        http_method=_truncate(method, MAX_METHOD_LENGTH) or "GET",
        endpoint=_truncate(endpoint, MAX_ENDPOINT_LENGTH),
        path=_truncate(request.path, MAX_PATH_LENGTH),
        action=_truncate(action, MAX_ACTION_LENGTH),
        action_type=_truncate(action_type, MAX_ACTION_LENGTH),
        is_sensitive=bool(is_sensitive),
        resource_type=_truncate(resource_type, MAX_RESOURCE_TYPE_LENGTH),
        resource_id=_truncate(resource_id, MAX_RESOURCE_ID_LENGTH),
        owner_id=context.owner_id,
        permission=_truncate(context.permission, MAX_PERMISSION_LENGTH),
        ownership_result=_truncate(context.ownership_result, MAX_OWNERSHIP_LENGTH),
        authorization_result=_truncate(authorization_result, MAX_AUTH_RESULT_LENGTH),
        status_code=response.status_code,
        response_time_ms=round(float(response_time_ms), 3),
        file_size=context.file_size,
        export_item_count=None,
        export_total_size=None,
    )


def save_request_log(response: Response, response_time_ms: float) -> None:
    """Persist one structured log row using an isolated DB session.

    The logger uses a short-lived SQLAlchemy session instead of Flask's main
    ``db.session``. This prevents a logging commit/rollback from accidentally
    committing or rolling back business data from the original request.

    Any exception must be handled by the middleware caller so logging can never
    break the user-facing request.
    """
    log_row = build_request_log(response, response_time_ms)
    session_factory = sessionmaker(bind=db.engine, expire_on_commit=False)
    log_session = session_factory()
    try:
        log_session.add(log_row)
        log_session.commit()
    except Exception:
        log_session.rollback()
        raise
    finally:
        log_session.close()
