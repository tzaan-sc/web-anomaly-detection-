from __future__ import annotations

from flask import abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy import func

from app.blueprints.admin import bp
from app.decorators.authorization import admin_required
from app.extensions import db
from app.models import FileShare, Folder, StoredFile, User
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

    query = StoredFile.query
    query, owner = _owner_filter(query, StoredFile)
    query, deleted = _deleted_filter(query, StoredFile)

    if extension:
        query = query.filter(StoredFile.file_extension == extension)

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
            page=page_number,
        )

    return render_template(
        "admin/files.html",
        files=pagination.items,
        pagination=pagination,
        owner=owner,
        deleted=deleted,
        extension=extension,
        extension_options=extension_options,
        page_url=page_url,
        format_file_size=format_file_size,
    )


@bp.get("/folders")
@admin_required
def folders():
    page = max(request.args.get("page", 1, type=int), 1)

    query = Folder.query
    query, owner = _owner_filter(query, Folder)
    query, deleted = _deleted_filter(query, Folder)

    pagination = query.order_by(Folder.created_at.desc(), Folder.id.desc()).paginate(
        page=page, per_page=15, error_out=False
    )

    def page_url(page_number: int) -> str:
        return url_for("admin.folders", owner=owner, deleted=deleted, page=page_number)

    return render_template(
        "admin/folders.html",
        folders=pagination.items,
        pagination=pagination,
        owner=owner,
        deleted=deleted,
        page_url=page_url,
    )
