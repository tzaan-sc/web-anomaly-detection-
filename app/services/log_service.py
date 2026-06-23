"""Helpers for structured request logging.

The service deliberately stores only request metadata. It must never persist
passwords, CSRF values, raw cookies, session tokens, request bodies, or file
contents.
"""

from __future__ import annotations

from typing import Any

from flask import g, request, session
from sqlalchemy.orm import sessionmaker
from werkzeug.wrappers import Response

from app.extensions import db
from app.models import RequestLog


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
    "documents.create_folder",
}


ACTION_BY_ENDPOINT = {
    "main.index": "home",
    "main.dashboard": "dashboard",
    "main.health": "health",
    "auth.login": "login",
    "auth.logout": "logout",
    "auth.profile": "profile",
    "auth.change_password": "change_password",
    "documents.legacy_index": "list",
    "documents.index": "list",
    "documents.browse_folder": "list",
    "documents.create_folder": "create_folder",
    "documents.upload_file": "upload",
    "documents.file_detail": "view_detail",
    "documents.download_file": "download",
    "documents.file_api": "api_view_detail",
    "documents.rename_file": "rename",
    "documents.move_file": "move",
    "documents.share_file": "share",
    "documents.revoke_share": "revoke_share",
    "documents.shared_with_me": "list_shared",
    "documents.trash": "trash",
    "documents.delete_file": "delete",
    "documents.restore_file": "restore",
    "documents.permanent_delete_file": "permanent_delete",
    "documents.export_files_csv": "export",
    "admin.index": "admin_dashboard",
    "admin.users": "admin_users",
    "admin.toggle_user_active": "admin_toggle_user",
    "admin.files": "admin_files",
    "admin.folders": "admin_folders",
}


SENSITIVE_ACTIONS = {
    "login",
    "logout",
    "change_password",
    "download",
    "share",
    "revoke_share",
    "delete",
    "restore",
    "permanent_delete",
    "export",
}


def _truncate(value: Any, max_length: int) -> str | None:
    """Return a string safely truncated for the database column."""
    if value is None:
        return None
    text = str(value)
    if not text:
        return None
    return text[:max_length]


def resolve_action(endpoint: str | None, method: str) -> str:
    """Map a Flask endpoint to a behavior action used by later ML features."""
    if endpoint in ACTION_BY_ENDPOINT:
        return ACTION_BY_ENDPOINT[endpoint]
    if endpoint and endpoint.startswith("admin."):
        return "admin"
    if method == "POST":
        return "write"
    return "other"


def resolve_resource(endpoint: str | None, view_args: dict[str, Any] | None) -> tuple[str | None, str | None]:
    """Extract resource type/id from route parameters without parsing raw URLs."""
    view_args = view_args or {}

    if endpoint in FILE_ENDPOINTS and "file_id" in view_args:
        return "file", str(view_args["file_id"])

    if endpoint in FOLDER_ENDPOINTS and "folder_id" in view_args:
        return "folder", str(view_args["folder_id"])

    if endpoint == "admin.toggle_user_active" and "user_id" in view_args:
        return "user", str(view_args["user_id"])

    if endpoint == "documents.revoke_share" and "share_id" in view_args:
        return "share", str(view_args["share_id"])

    return None, None


def resolve_authorization_result(status_code: int) -> str:
    """Convert status code to a coarse authorization/logging result."""
    if status_code in {401, 403, 404}:
        return "denied"
    if 200 <= status_code < 400:
        return "allowed"
    return "error"


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
    resource_type, resource_id = resolve_resource(endpoint, request.view_args)

    current_user = g.get("current_user")
    session_user_id = session.get("user_id")
    session_role = session.get("role")

    user_id = getattr(current_user, "id", None) or session_user_id
    role = getattr(current_user, "role", None) or session_role

    session_id_hash = session.get("session_id_hash")

    # Do not touch request.form, request.get_json(), request.data, cookies,
    # uploaded file streams, CSRF tokens, or passwords here.
    return RequestLog(
        request_id=_truncate(g.get("request_id"), 64),
        user_id=user_id,
        role=_truncate(role, MAX_ROLE_LENGTH),
        session_id_hash=_truncate(session_id_hash, MAX_SESSION_HASH_LENGTH),
        ip_address=get_client_ip(),
        user_agent=_truncate(request.headers.get("User-Agent"), MAX_USER_AGENT_LENGTH),
        http_method=_truncate(method, MAX_METHOD_LENGTH) or "GET",
        endpoint=_truncate(endpoint, MAX_ENDPOINT_LENGTH),
        path=_truncate(request.path, MAX_PATH_LENGTH),
        action=_truncate(action, MAX_ACTION_LENGTH),
        resource_type=_truncate(resource_type, MAX_RESOURCE_TYPE_LENGTH),
        resource_id=_truncate(resource_id, MAX_RESOURCE_ID_LENGTH),
        permission=None,
        authorization_result=_truncate(
            resolve_authorization_result(response.status_code), MAX_AUTH_RESULT_LENGTH
        ),
        status_code=response.status_code,
        response_time_ms=round(float(response_time_ms), 3),
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


def is_sensitive_action(endpoint: str | None, method: str) -> bool:
    """Small helper for tests/manual checks; it does not persist raw data."""
    return resolve_action(endpoint, method) in SENSITIVE_ACTIONS
