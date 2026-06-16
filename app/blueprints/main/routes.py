from datetime import UTC, datetime

from flask import g, jsonify, redirect, render_template, url_for

from app.blueprints.main import bp
from app.decorators.authorization import login_required
from app.models import FileShare, Folder, StoredFile


@bp.get("/")
def index():
    if g.current_user is not None:
        if g.current_user.is_admin:
            return redirect(url_for("admin.index"))

        return redirect(url_for("main.dashboard"))

    return render_template("main/index.html")


@bp.get("/dashboard")
@login_required
def dashboard():
    user_id = g.current_user.id

    owned_file_count = StoredFile.query.filter_by(
        owner_id=user_id,
        is_deleted=False,
    ).count()

    folder_count = Folder.query.filter_by(
        owner_id=user_id,
        is_deleted=False,
    ).count()

    shared_file_count = (
        FileShare.query
        .join(StoredFile, FileShare.file_id == StoredFile.id)
        .filter(
            FileShare.shared_with_user_id == user_id,
            FileShare.revoked_at.is_(None),
            StoredFile.is_deleted.is_(False),
        )
        .count()
    )

    trash_file_count = StoredFile.query.filter_by(
        owner_id=user_id,
        is_deleted=True,
    ).count()

    recent_files = (
        StoredFile.query
        .filter_by(
            owner_id=user_id,
            is_deleted=False,
        )
        .order_by(StoredFile.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "main/dashboard.html",
        owned_file_count=owned_file_count,
        folder_count=folder_count,
        shared_file_count=shared_file_count,
        trash_file_count=trash_file_count,
        recent_files=recent_files,
    )


@bp.get("/health")
def health():
    return (
        jsonify(
            status="ok",
            service="studydrive",
            timestamp=datetime.now(UTC).isoformat(),
        ),
        200,
    )