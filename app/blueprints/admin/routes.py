from __future__ import annotations

from flask import abort, current_app, flash, g, redirect, render_template, request, url_for
from datetime import datetime, timezone
import csv
import io

from sqlalchemy import func

from app.blueprints.admin import bp
from app.decorators.authorization import admin_required
from app.extensions import db
from app.models import FileShare, Folder, RequestLog, StoredFile, User
from app.services.document_service import format_file_size


@bp.get("/")
@admin_required
def index():
    user_count = User.query.count()
    active_user_count = User.query.filter_by(is_active=True).count()
    file_count = StoredFile.query.count()
    active_file_count = StoredFile.query.filter_by(is_deleted=False).count()
    deleted_file_count = StoredFile.query.filter_by(is_deleted=True).count()
    folder_count = Folder.query.count()
    share_count = FileShare.query.filter_by(revoked_at=None).count()

    recent_files = StoredFile.query.order_by(StoredFile.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template(
        "admin/index.html",
        user_count=user_count,
        active_user_count=active_user_count,
        file_count=file_count,
        active_file_count=active_file_count,
        deleted_file_count=deleted_file_count,
        folder_count=folder_count,
        share_count=share_count,
        recent_files=recent_files,
        recent_users=recent_users,
        format_file_size=format_file_size,
    )


@bp.get("/users")
@admin_required
def users():
    search_text = request.args.get("q", "", type=str).strip()[:255]
    page = max(request.args.get("page", 1, type=int), 1)

    query = User.query
    if search_text:
        escaped = search_text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped.lower()}%"
        query = query.filter(
            func.lower(User.username).like(pattern, escape="\\")
            | func.lower(User.email).like(pattern, escape="\\")
            | func.lower(User.role).like(pattern, escape="\\")
        )

    pagination = query.order_by(User.id.asc()).paginate(page=page, per_page=10, error_out=False)

    def page_url(page_number: int) -> str:
        return url_for("admin.users", q=search_text, page=page_number)

    return render_template(
        "admin/users.html",
        users=pagination.items,
        pagination=pagination,
        search_text=search_text,
        page_url=page_url,
    )


@bp.post("/users/<int:user_id>/toggle-active")
@admin_required
def toggle_user_active(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == g.current_user.id:
        flash("Không thể tự khóa tài khoản admin đang đăng nhập.", "warning")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    db.session.commit()
    status = "mở khóa" if user.is_active else "khóa"
    flash(f"Đã {status} tài khoản {user.username}.", "success")
    return redirect(request.referrer or url_for("admin.users"))


def _owner_filter(query, model):
    owner = request.args.get("owner", "", type=str).strip()[:255]
    if not owner:
        return query, owner

    if owner.isdigit():
        query = query.filter(model.owner_id == int(owner))
    else:
        escaped = owner.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.join(User, model.owner_id == User.id).filter(
            func.lower(User.username).like(f"%{escaped.lower()}%", escape="\\")
        )
    return query, owner


def _deleted_filter(query, model):
    deleted = request.args.get("deleted", "active", type=str)
    if deleted == "yes":
        query = query.filter(model.is_deleted.is_(True))
    elif deleted == "all":
        pass
    else:
        deleted = "active"
        query = query.filter(model.is_deleted.is_(False))
    return query, deleted


@bp.get("/files")
@admin_required
def files():
    page = max(request.args.get("page", 1, type=int), 1)
    extension = request.args.get("extension", "", type=str).strip().lower()[:20]
    file_id = request.args.get("file_id", "", type=str).strip()[:30]

    query = StoredFile.query
    query, owner = _owner_filter(query, StoredFile)
    query, deleted = _deleted_filter(query, StoredFile)

    if extension:
        query = query.filter(StoredFile.file_extension == extension)

    if file_id:
        if not file_id.isdigit():
            abort(400)
        query = query.filter(StoredFile.id == int(file_id))

    pagination = query.order_by(StoredFile.created_at.desc(), StoredFile.id.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    extension_options = [
        row[0]
        for row in StoredFile.query.with_entities(StoredFile.file_extension)
        .distinct()
        .order_by(StoredFile.file_extension.asc())
        .all()
        if row[0]
    ]

    def page_url(page_number: int) -> str:
        return url_for(
            "admin.files",
            owner=owner,
            deleted=deleted,
            extension=extension,
            file_id=file_id,
            page=page_number,
        )

    return render_template(
        "admin/files.html",
        files=pagination.items,
        pagination=pagination,
        owner=owner,
        deleted=deleted,
        extension=extension,
        file_id=file_id,
        extension_options=extension_options,
        page_url=page_url,
        format_file_size=format_file_size,
    )


@bp.get("/folders")
@admin_required
def folders():
    page = max(request.args.get("page", 1, type=int), 1)
    folder_id = request.args.get("folder_id", "", type=str).strip()[:30]

    query = Folder.query
    query, owner = _owner_filter(query, Folder)
    query, deleted = _deleted_filter(query, Folder)

    if folder_id:
        if not folder_id.isdigit():
            abort(400)
        query = query.filter(Folder.id == int(folder_id))

    pagination = query.order_by(Folder.created_at.desc(), Folder.id.desc()).paginate(
        page=page, per_page=15, error_out=False
    )

    def page_url(page_number: int) -> str:
        return url_for("admin.folders", owner=owner, deleted=deleted, folder_id=folder_id, page=page_number)

    return render_template(
        "admin/folders.html",
        folders=pagination.items,
        pagination=pagination,
        owner=owner,
        deleted=deleted,
        folder_id=folder_id,
        page_url=page_url,
    )


# -----------------------------
# Admin request log management
# -----------------------------

LOG_SORT_OPTIONS = {
    "newest": ("Mới nhất", lambda: (RequestLog.timestamp.desc(), RequestLog.id.desc())),
    "oldest": ("Cũ nhất", lambda: (RequestLog.timestamp.asc(), RequestLog.id.asc())),
    "slowest": ("Chậm nhất", lambda: (RequestLog.response_time_ms.desc(), RequestLog.id.desc())),
    "fastest": ("Nhanh nhất", lambda: (RequestLog.response_time_ms.asc(), RequestLog.id.asc())),
    "status_desc": ("Status cao → thấp", lambda: (RequestLog.status_code.desc(), RequestLog.id.desc())),
    "action_asc": ("Action A → Z", lambda: (RequestLog.action_type.asc(), RequestLog.id.desc())),
}

LOG_CSV_COLUMNS = [
    "id",
    "request_id",
    "timestamp",
    "user_id",
    "username",
    "is_authenticated",
    "role",
    "session_id_hash",
    "ip_address",
    "user_agent",
    "http_method",
    "endpoint",
    "path",
    "action",
    "action_type",
    "is_sensitive",
    "resource_type",
    "resource_id",
    "owner_id",
    "permission",
    "ownership_result",
    "authorization_result",
    "status_code",
    "response_time_ms",
    "file_size",
    "export_item_count",
    "export_total_size",
]


def _parse_datetime_filter(raw_value: str | None):
    """Parse date/datetime-local values from the admin filter form."""
    value = (raw_value or "").strip()
    if not value:
        return None
    try:
        if len(value) == 10:
            return datetime.fromisoformat(value)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        abort(400)


def _log_filter_values() -> dict[str, str]:
    return {
        "start": request.args.get("start", "", type=str).strip()[:40],
        "end": request.args.get("end", "", type=str).strip()[:40],
        "user": request.args.get("user", "", type=str).strip()[:255],
        "action_type": request.args.get("action_type", "", type=str).strip()[:80],
        "status_code": request.args.get("status_code", "", type=str).strip()[:10],
        "sensitive": request.args.get("sensitive", "", type=str).strip().lower()[:10],
        "path_keyword": request.args.get("path_keyword", "", type=str).strip()[:255],
        "sort": request.args.get("sort", "newest", type=str).strip()[:30],
    }


def _apply_log_filters(query, filters: dict[str, str]):
    start_dt = _parse_datetime_filter(filters["start"])
    end_dt = _parse_datetime_filter(filters["end"])
    if start_dt is not None:
        query = query.filter(RequestLog.timestamp >= start_dt)
    if end_dt is not None:
        query = query.filter(RequestLog.timestamp <= end_dt)

    user_value = filters["user"]
    if user_value:
        if user_value.isdigit():
            query = query.filter(RequestLog.user_id == int(user_value))
        else:
            escaped = user_value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped.lower()}%"
            query = query.outerjoin(User, RequestLog.user_id == User.id).filter(
                func.lower(User.username).like(pattern, escape="\\")
                | func.lower(User.email).like(pattern, escape="\\")
            )

    if filters["action_type"]:
        query = query.filter(RequestLog.action_type == filters["action_type"])

    if filters["status_code"]:
        if not filters["status_code"].isdigit():
            abort(400)
        query = query.filter(RequestLog.status_code == int(filters["status_code"]))

    if filters["sensitive"] == "yes":
        query = query.filter(RequestLog.is_sensitive.is_(True))
    elif filters["sensitive"] == "no":
        query = query.filter(RequestLog.is_sensitive.is_(False))
    elif filters["sensitive"] not in {"", "all"}:
        abort(400)

    if filters["path_keyword"]:
        escaped = filters["path_keyword"].replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(RequestLog.path.like(f"%{escaped}%", escape="\\"))

    return query


def _filtered_logs_query(filters: dict[str, str]):
    sort_key = filters.get("sort") or "newest"
    if sort_key not in LOG_SORT_OPTIONS:
        sort_key = "newest"
        filters["sort"] = sort_key

    query = RequestLog.query
    query = _apply_log_filters(query, filters)
    return query.order_by(*LOG_SORT_OPTIONS[sort_key][1]())


def _timestamp_for_display(value) -> str:
    if value is None:
        return ""
    try:
        return value.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return str(value)


def _timestamp_for_csv(value) -> str:
    if value is None:
        return ""
    try:
        return value.isoformat()
    except Exception:
        return str(value)


def _log_to_csv_row(log: RequestLog) -> dict[str, object]:
    return {
        "id": log.id,
        "request_id": log.request_id,
        "timestamp": _timestamp_for_csv(log.timestamp),
        "user_id": log.user_id,
        "username": log.user.username if log.user else "",
        "is_authenticated": int(bool(log.is_authenticated)),
        "role": log.role or "",
        "session_id_hash": log.session_id_hash or "",
        "ip_address": log.ip_address or "",
        "user_agent": log.user_agent or "",
        "http_method": log.http_method or "",
        "endpoint": log.endpoint or "",
        "path": log.path or "",
        "action": log.action or "",
        "action_type": log.action_type or "",
        "is_sensitive": int(bool(log.is_sensitive)),
        "resource_type": log.resource_type or "",
        "resource_id": log.resource_id or "",
        "owner_id": log.owner_id if log.owner_id is not None else "",
        "permission": log.permission or "",
        "ownership_result": log.ownership_result or "",
        "authorization_result": log.authorization_result or "",
        "status_code": log.status_code,
        "response_time_ms": log.response_time_ms,
        "file_size": log.file_size if log.file_size is not None else "",
        "export_item_count": log.export_item_count if log.export_item_count is not None else "",
        "export_total_size": log.export_total_size if log.export_total_size is not None else "",
    }


@bp.get("/logs")
@admin_required
def logs():
    filters = _log_filter_values()
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 25, type=int), 10), 100)

    query = _filtered_logs_query(filters)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    action_type_options = [
        row[0]
        for row in RequestLog.query.with_entities(RequestLog.action_type)
        .filter(RequestLog.action_type.isnot(None))
        .distinct()
        .order_by(RequestLog.action_type.asc())
        .all()
        if row[0]
    ]
    status_options = [
        row[0]
        for row in RequestLog.query.with_entities(RequestLog.status_code)
        .distinct()
        .order_by(RequestLog.status_code.asc())
        .all()
        if row[0] is not None
    ]

    base_args = request.args.to_dict(flat=True)
    base_args.pop("page", None)

    def page_url(page_number: int) -> str:
        return url_for("admin.logs", **base_args, page=page_number)

    return render_template(
        "admin/logs.html",
        logs=pagination.items,
        pagination=pagination,
        filters=filters,
        per_page=per_page,
        page_url=page_url,
        export_url=url_for("admin.logs_export", **base_args),
        action_type_options=action_type_options,
        status_options=status_options,
        sort_options=[(key, label) for key, (label, _order) in LOG_SORT_OPTIONS.items()],
        timestamp_for_display=_timestamp_for_display,
    )


@bp.get("/logs/<int:log_id>")
@admin_required
def log_detail(log_id: int):
    log = db.session.get(RequestLog, log_id)
    if log is None:
        abort(404)

    related_user_url = None
    if log.user is not None:
        related_user_url = url_for("admin.users", q=log.user.username)

    related_file = None
    related_file_url = None
    related_folder = None
    related_folder_url = None
    if log.resource_type == "file" and log.resource_id and log.resource_id.isdigit():
        related_file = db.session.get(StoredFile, int(log.resource_id))
        if related_file is not None:
            related_file_url = url_for("admin.files", file_id=related_file.id, deleted="all")
    elif log.resource_type == "folder" and log.resource_id and log.resource_id.isdigit():
        related_folder = db.session.get(Folder, int(log.resource_id))
        if related_folder is not None:
            related_folder_url = url_for("admin.folders", folder_id=related_folder.id, deleted="all")

    return render_template(
        "admin/log_detail.html",
        log=log,
        related_user_url=related_user_url,
        related_file=related_file,
        related_file_url=related_file_url,
        related_folder=related_folder,
        related_folder_url=related_folder_url,
        timestamp_for_display=_timestamp_for_display,
        format_file_size=format_file_size,
    )


@bp.get("/logs/export")
@admin_required
def logs_export():
    filters = _log_filter_values()
    query = _filtered_logs_query(filters)
    max_rows = min(max(request.args.get("max_rows", 50000, type=int), 1), 200000)
    rows = query.limit(max_rows).all()

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=LOG_CSV_COLUMNS)
    writer.writeheader()
    for log in rows:
        writer.writerow(_log_to_csv_row(log))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"request_logs_filtered_{timestamp}.csv"
    response = current_app.response_class(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
    )
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"
    response.headers["X-Exported-Log-Rows"] = str(len(rows))
    return response
