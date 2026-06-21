"""Routes for StudyDrive folders, files, sharing, and authorization."""

from __future__ import annotations

from flask import (
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from sqlalchemy import func

from app.blueprints.documents import bp
from app.blueprints.documents.forms import (
    CreateFolderForm,
    MoveFileForm,
    RenameFileForm,
    ShareFileForm,
    UploadFileForm,
)
from app.decorators.authorization import login_required
from app.extensions import db
from app.models import FileShare, Folder, StoredFile, User
from app.services.document_service import (
    ACCESS_NONE,
    ACCESS_OWNER,
    DocumentValidationError,
    active_folder_choices,
    can_modify_file,
    can_view_file,
    create_folder as create_folder_record,
    folder_breadcrumb,
    format_file_size,
    get_file_access,
    get_owned_folder,
    move_file as move_file_record,
    rename_file as rename_file_record,
    resolve_physical_file,
    revoke_file_share,
    save_uploaded_file,
    share_file as share_file_record,
    share_recipient_choices,
)


SORT_OPTIONS = {
    "newest": ("Mới cập nhật", lambda: (StoredFile.updated_at.desc(), StoredFile.id.desc())),
    "oldest": ("Cũ nhất", lambda: (StoredFile.updated_at.asc(), StoredFile.id.asc())),
    "name_asc": (
        "Tên A → Z",
        lambda: (func.lower(StoredFile.original_name).asc(), StoredFile.id.asc()),
    ),
    "name_desc": (
        "Tên Z → A",
        lambda: (func.lower(StoredFile.original_name).desc(), StoredFile.id.desc()),
    ),
    "size_asc": ("Kích thước tăng", lambda: (StoredFile.file_size.asc(), StoredFile.id.asc())),
    "size_desc": ("Kích thước giảm", lambda: (StoredFile.file_size.desc(), StoredFile.id.desc())),
}


def _folder_or_404(folder_id: int) -> Folder:
    folder = get_owned_folder(folder_id, g.current_user.id)
    if folder is None:
        # 404 avoids confirming that another user's folder exists.
        abort(404)
    return folder


def _file_record(file_id: int) -> StoredFile | None:
    return db.session.get(StoredFile, file_id)


def _viewable_file_or_404(file_id: int) -> tuple[StoredFile, str]:
    stored_file = _file_record(file_id)
    if not can_view_file(stored_file, g.current_user.id):
        # StudyDrive consistently hides missing, deleted, and unauthorized files.
        abort(404)
    return stored_file, get_file_access(stored_file, g.current_user.id)


def _owned_file_or_404(file_id: int) -> StoredFile:
    stored_file = _file_record(file_id)
    if not can_modify_file(stored_file, g.current_user.id):
        abort(404)
    return stored_file


def _render_file_list(current_folder: Folder | None = None):
    user_id = g.current_user.id
    search_text = request.args.get("q", "", type=str).strip()[:255]
    extension = request.args.get("extension", "", type=str).strip().lower()[:20]
    sort_key = request.args.get("sort", "newest", type=str)
    if sort_key not in SORT_OPTIONS:
        sort_key = "newest"

    query = StoredFile.query.filter(
        StoredFile.owner_id == user_id,
        StoredFile.is_deleted.is_(False),
    )

    selected_folder_filter = request.args.get("folder", "", type=str).strip()
    selected_filter_folder: Folder | None = None
    if current_folder is not None:
        query = query.filter(StoredFile.folder_id == current_folder.id)
        selected_folder_filter = str(current_folder.id)
    elif selected_folder_filter == "root":
        query = query.filter(StoredFile.folder_id.is_(None))
    elif selected_folder_filter:
        try:
            filter_folder_id = int(selected_folder_filter)
        except ValueError:
            abort(400)
        selected_filter_folder = get_owned_folder(filter_folder_id, user_id)
        if selected_filter_folder is None:
            abort(404)
        query = query.filter(StoredFile.folder_id == selected_filter_folder.id)

    if search_text:
        escaped_search = (
            search_text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        )
        query = query.filter(
            func.lower(StoredFile.original_name).like(
                f"%{escaped_search.lower()}%", escape="\\"
            )
        )

    allowed_extensions = {
        value.lower() for value in current_app.config.get("ALLOWED_EXTENSIONS", set())
    }
    if extension:
        if extension not in allowed_extensions:
            abort(400)
        query = query.filter(StoredFile.file_extension == extension)

    query = query.order_by(*SORT_OPTIONS[sort_key][1]())
    page = max(request.args.get("page", 1, type=int), 1)
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    child_parent_id = current_folder.id if current_folder else None
    child_folders = (
        Folder.query.filter_by(
            owner_id=user_id,
            parent_id=child_parent_id,
            is_deleted=False,
        )
        .order_by(func.lower(Folder.name).asc())
        .all()
    )

    extension_rows = (
        StoredFile.query.with_entities(StoredFile.file_extension)
        .filter(
            StoredFile.owner_id == user_id,
            StoredFile.is_deleted.is_(False),
        )
        .distinct()
        .order_by(StoredFile.file_extension.asc())
        .all()
    )
    extension_options = [row[0] for row in extension_rows if row[0]]

    folder_choices = active_folder_choices(user_id)
    folder_filter_options = [
        ("", "Tất cả thư mục"),
        ("root", "Chỉ thư mục gốc"),
        *[(str(folder_id), label) for folder_id, label in folder_choices if folder_id != 0],
    ]

    base_args = request.args.to_dict(flat=True)
    base_args.pop("page", None)
    route_values = {"folder_id": current_folder.id} if current_folder else {}

    def page_url(page_number: int) -> str:
        return url_for(
            request.endpoint,
            **route_values,
            **base_args,
            page=page_number,
        )

    return render_template(
        "documents/index.html",
        current_folder=current_folder,
        breadcrumb=folder_breadcrumb(current_folder),
        child_folders=child_folders,
        files=pagination.items,
        pagination=pagination,
        page_url=page_url,
        search_text=search_text,
        selected_extension=extension,
        selected_folder_filter=selected_folder_filter,
        selected_filter_folder=selected_filter_folder,
        sort_key=sort_key,
        sort_options=[(key, label) for key, (label, _) in SORT_OPTIONS.items()],
        extension_options=extension_options,
        folder_filter_options=folder_filter_options,
        format_file_size=format_file_size,
    )


@bp.get("/documents/")
@login_required
def legacy_index():
    """Keep the old route usable while the canonical route is /files."""
    return redirect(url_for("documents.index"))


@bp.get("/files")
@login_required
def index():
    return _render_file_list()


@bp.get("/folders/<int:folder_id>")
@login_required
def browse_folder(folder_id: int):
    return _render_file_list(_folder_or_404(folder_id))


@bp.route("/folders/create", methods=["GET", "POST"])
@login_required
def create_folder():
    form = CreateFolderForm()
    form.parent_id.choices = active_folder_choices(g.current_user.id)

    requested_parent_id = request.args.get("parent_id", 0, type=int)
    if request.method == "GET" and requested_parent_id:
        if get_owned_folder(requested_parent_id, g.current_user.id) is None:
            abort(404)
        form.parent_id.data = requested_parent_id

    submitted_parent = None
    if request.method == "POST":
        raw_parent_id = request.form.get("parent_id", "0")
        try:
            submitted_parent_id = int(raw_parent_id)
        except (TypeError, ValueError):
            abort(400)
        if submitted_parent_id:
            submitted_parent = get_owned_folder(submitted_parent_id, g.current_user.id)
            if submitted_parent is None:
                abort(404)

    if form.validate_on_submit():
        try:
            folder = create_folder_record(
                owner=g.current_user,
                name=form.name.data,
                parent=submitted_parent,
            )
        except DocumentValidationError as exc:
            form.name.errors.append(str(exc))
        except Exception:
            current_app.logger.exception("Không thể tạo thư mục")
            flash("Không thể tạo thư mục. Dữ liệu chưa được lưu.", "danger")
        else:
            flash(f"Đã tạo thư mục “{folder.name}” thành công.", "success")
            if submitted_parent is not None:
                return redirect(
                    url_for("documents.browse_folder", folder_id=submitted_parent.id)
                )
            return redirect(url_for("documents.index"))

    return render_template("documents/create_folder.html", form=form)


@bp.route("/files/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    form = UploadFileForm()
    form.folder_id.choices = active_folder_choices(g.current_user.id)

    requested_folder_id = request.args.get("folder_id", 0, type=int)
    if request.method == "GET" and requested_folder_id:
        if get_owned_folder(requested_folder_id, g.current_user.id) is None:
            abort(404)
        form.folder_id.data = requested_folder_id

    submitted_folder = None
    if request.method == "POST":
        raw_folder_id = request.form.get("folder_id", "0")
        try:
            submitted_folder_id = int(raw_folder_id)
        except (TypeError, ValueError):
            abort(400)
        if submitted_folder_id:
            submitted_folder = get_owned_folder(submitted_folder_id, g.current_user.id)
            if submitted_folder is None:
                abort(404)

    if form.validate_on_submit():
        try:
            stored_file = save_uploaded_file(
                file_storage=form.file.data,
                owner=g.current_user,
                folder=submitted_folder,
            )
        except DocumentValidationError as exc:
            form.file.errors.append(str(exc))
        except Exception:
            current_app.logger.exception("Upload thất bại; đã rollback và dọn file rác")
            flash(
                "Upload thất bại. Metadata đã rollback và file tạm đã được dọn.",
                "danger",
            )
        else:
            flash(f"Đã upload “{stored_file.original_name}” thành công.", "success")
            if submitted_folder is not None:
                return redirect(
                    url_for("documents.browse_folder", folder_id=submitted_folder.id)
                )
            return redirect(url_for("documents.index"))

    return render_template(
        "documents/upload.html",
        form=form,
        max_size_mb=current_app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024),
        allowed_extensions=sorted(current_app.config["ALLOWED_EXTENSIONS"]),
    )


@bp.get("/files/<int:file_id>")
@login_required
def file_detail(file_id: int):
    stored_file, access = _viewable_file_or_404(file_id)
    active_shares = []
    if access == ACCESS_OWNER:
        active_shares = (
            FileShare.query.filter_by(
                file_id=stored_file.id,
                permission="VIEWER",
                revoked_at=None,
            )
            .order_by(FileShare.created_at.desc())
            .all()
        )

    return render_template(
        "documents/detail.html",
        file=stored_file,
        access=access,
        active_shares=active_shares,
        format_file_size=format_file_size,
    )


@bp.get("/files/<int:file_id>/download")
@login_required
def download_file(file_id: int):
    stored_file, _access = _viewable_file_or_404(file_id)
    try:
        physical_path = resolve_physical_file(stored_file)
    except FileNotFoundError:
        current_app.logger.warning(
            "Physical file missing or unsafe for file_id=%s", stored_file.id
        )
        abort(404)

    return send_file(
        physical_path,
        as_attachment=True,
        download_name=stored_file.original_name,
        mimetype=stored_file.mime_type,
        conditional=True,
        max_age=0,
    )


@bp.get("/api/files/<int:file_id>")
@login_required
def file_api(file_id: int):
    stored_file = _file_record(file_id)
    if not can_view_file(stored_file, g.current_user.id):
        # JSON 404 has the same body for nonexistent and unauthorized IDs.
        return jsonify({"error": "file_not_found"}), 404
    access = get_file_access(stored_file, g.current_user.id)

    payload = {
        "id": stored_file.id,
        "original_name": stored_file.original_name,
        "file_extension": stored_file.file_extension,
        "mime_type": stored_file.mime_type,
        "file_size": stored_file.file_size,
        "access": access,
        "owner": {"id": stored_file.owner_id, "username": stored_file.owner.username},
        "created_at": stored_file.created_at.isoformat(),
        "updated_at": stored_file.updated_at.isoformat(),
    }
    if access == ACCESS_OWNER:
        payload["folder"] = (
            {"id": stored_file.folder.id, "name": stored_file.folder.name}
            if stored_file.folder is not None
            else None
        )
    return jsonify(payload)


@bp.route("/files/<int:file_id>/rename", methods=["GET", "POST"])
@login_required
def rename_file(file_id: int):
    stored_file = _owned_file_or_404(file_id)
    form = RenameFileForm()
    if request.method == "GET":
        form.original_name.data = stored_file.original_name

    if form.validate_on_submit():
        try:
            rename_file_record(
                stored_file=stored_file,
                owner=g.current_user,
                new_name=form.original_name.data,
            )
        except DocumentValidationError as exc:
            form.original_name.errors.append(str(exc))
        except Exception:
            current_app.logger.exception("Không thể đổi tên file_id=%s", file_id)
            flash("Không thể đổi tên tệp. Dữ liệu chưa thay đổi.", "danger")
        else:
            flash("Đã đổi tên tệp. Tên UUID lưu trên server không thay đổi.", "success")
            return redirect(url_for("documents.file_detail", file_id=file_id))

    return render_template("documents/rename.html", form=form, file=stored_file)


@bp.route("/files/<int:file_id>/move", methods=["GET", "POST"])
@login_required
def move_file(file_id: int):
    stored_file = _owned_file_or_404(file_id)
    form = MoveFileForm()
    form.folder_id.choices = active_folder_choices(g.current_user.id)
    if request.method == "GET":
        form.folder_id.data = stored_file.folder_id or 0

    target_folder = None
    if request.method == "POST":
        raw_folder_id = request.form.get("folder_id", "0")
        try:
            submitted_folder_id = int(raw_folder_id)
        except (TypeError, ValueError):
            abort(400)
        if submitted_folder_id:
            target_folder = get_owned_folder(submitted_folder_id, g.current_user.id)
            if target_folder is None:
                abort(404)

    if form.validate_on_submit():
        try:
            move_file_record(
                stored_file=stored_file,
                owner=g.current_user,
                target_folder=target_folder,
            )
        except DocumentValidationError as exc:
            form.folder_id.errors.append(str(exc))
        except Exception:
            current_app.logger.exception("Không thể di chuyển file_id=%s", file_id)
            flash("Không thể di chuyển tệp. Dữ liệu chưa thay đổi.", "danger")
        else:
            destination = target_folder.name if target_folder else "My Drive"
            flash(f"Đã di chuyển tệp đến “{destination}”.", "success")
            return redirect(url_for("documents.file_detail", file_id=file_id))

    return render_template("documents/move.html", form=form, file=stored_file)


@bp.route("/files/<int:file_id>/share", methods=["GET", "POST"])
@login_required
def share_file(file_id: int):
    stored_file = _owned_file_or_404(file_id)
    form = ShareFileForm()
    form.recipient_id.choices = share_recipient_choices(g.current_user.id)

    recipient = None
    if request.method == "POST":
        raw_recipient_id = request.form.get("recipient_id", "")
        try:
            recipient_id = int(raw_recipient_id)
        except (TypeError, ValueError):
            abort(400)
        recipient = db.session.get(User, recipient_id)
        if recipient is None:
            abort(404)

    if form.validate_on_submit():
        try:
            share_file_record(
                stored_file=stored_file,
                owner=g.current_user,
                recipient=recipient,
            )
        except DocumentValidationError as exc:
            form.recipient_id.errors.append(str(exc))
        except Exception:
            current_app.logger.exception("Không thể share file_id=%s", file_id)
            flash("Không thể chia sẻ tệp. Dữ liệu chưa thay đổi.", "danger")
        else:
            flash(
                f"Đã chia sẻ “{stored_file.original_name}” cho {recipient.username} với quyền VIEWER.",
                "success",
            )
            return redirect(url_for("documents.file_detail", file_id=file_id))

    return render_template("documents/share.html", form=form, file=stored_file)


@bp.post("/files/<int:file_id>/shares/<int:share_id>/revoke")
@login_required
def revoke_share(file_id: int, share_id: int):
    stored_file = _owned_file_or_404(file_id)
    share = FileShare.query.filter_by(id=share_id, file_id=stored_file.id).first()
    if share is None or share.revoked_at is not None:
        abort(404)

    try:
        revoke_file_share(
            stored_file=stored_file,
            owner=g.current_user,
            share=share,
        )
    except DocumentValidationError:
        abort(404)
    except Exception:
        current_app.logger.exception("Không thể thu hồi share_id=%s", share_id)
        flash("Không thể thu hồi quyền chia sẻ.", "danger")
    else:
        flash(
            f"Đã thu hồi quyền VIEWER của {share.shared_with_user.username}.",
            "success",
        )
    return redirect(url_for("documents.file_detail", file_id=file_id))


@bp.get("/shared-with-me")
@login_required
def shared_with_me():
    page = max(request.args.get("page", 1, type=int), 1)
    query = (
        FileShare.query.join(StoredFile, FileShare.file_id == StoredFile.id)
        .filter(
            FileShare.shared_with_user_id == g.current_user.id,
            FileShare.permission == "VIEWER",
            FileShare.revoked_at.is_(None),
            StoredFile.is_deleted.is_(False),
        )
        .order_by(FileShare.created_at.desc(), FileShare.id.desc())
    )
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    return render_template(
        "documents/shared_with_me.html",
        shares=pagination.items,
        pagination=pagination,
        format_file_size=format_file_size,
    )


@bp.get("/trash")
@login_required
def trash():
    page = max(request.args.get("page", 1, type=int), 1)
    pagination = (
        StoredFile.query.filter_by(owner_id=g.current_user.id, is_deleted=True)
        .order_by(StoredFile.deleted_at.desc(), StoredFile.id.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    return render_template(
        "documents/trash.html",
        files=pagination.items,
        pagination=pagination,
        format_file_size=format_file_size,
    )


@bp.post("/files/<int:file_id>/delete")
@login_required
def delete_file(file_id: int):
    from app.services.document_service import soft_delete_file

    stored_file = _file_record(file_id)
    try:
        soft_delete_file(stored_file=stored_file, owner=g.current_user)
    except PermissionError:
        abort(404)
    except Exception:
        current_app.logger.exception("Không thể soft delete file_id=%s", file_id)
        flash("Không thể đưa tệp vào thùng rác.", "danger")
        return redirect(url_for("documents.file_detail", file_id=file_id))

    flash("Đã đưa tệp vào thùng rác. Bạn có thể khôi phục tại mục Thùng rác.", "success")
    return redirect(url_for("documents.index"))


@bp.post("/files/<int:file_id>/restore")
@login_required
def restore_file(file_id: int):
    from app.services.document_service import restore_file as restore_file_record

    stored_file = _file_record(file_id)
    try:
        restore_file_record(stored_file=stored_file, owner=g.current_user)
    except PermissionError:
        abort(404)
    except Exception:
        current_app.logger.exception("Không thể restore file_id=%s", file_id)
        flash("Không thể khôi phục tệp.", "danger")
    else:
        flash("Đã khôi phục tệp về My Drive.", "success")
    return redirect(url_for("documents.trash"))


@bp.post("/files/<int:file_id>/permanent-delete")
@login_required
def permanent_delete_file(file_id: int):
    from app.services.document_service import permanently_delete_file

    stored_file = _file_record(file_id)
    try:
        permanently_delete_file(stored_file=stored_file, owner=g.current_user)
    except PermissionError:
        abort(404)
    except DocumentValidationError as exc:
        flash(str(exc), "warning")
    except Exception:
        current_app.logger.exception("Không thể xóa vĩnh viễn file_id=%s", file_id)
        flash("Không thể xóa vĩnh viễn tệp.", "danger")
    else:
        flash("Đã xóa vĩnh viễn tệp khỏi thùng rác.", "success")
    return redirect(url_for("documents.trash"))


def _apply_export_filters(query):
    """Apply My Drive filters to an owner-only export query."""
    search_text = request.values.get("q", "", type=str).strip()[:255]
    extension = request.values.get("extension", "", type=str).strip().lower()[:20]
    folder_value = request.values.get("folder", "", type=str).strip()

    if search_text:
        escaped_search = search_text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(
            func.lower(StoredFile.original_name).like(
                f"%{escaped_search.lower()}%", escape="\\"
            )
        )

    if extension:
        allowed_extensions = {
            value.lower() for value in current_app.config.get("ALLOWED_EXTENSIONS", set())
        }
        if extension not in allowed_extensions:
            abort(400)
        query = query.filter(StoredFile.file_extension == extension)

    if folder_value == "root":
        query = query.filter(StoredFile.folder_id.is_(None))
    elif folder_value:
        try:
            folder_id = int(folder_value)
        except ValueError:
            abort(400)
        folder = get_owned_folder(folder_id, g.current_user.id)
        if folder is None:
            abort(404)
        query = query.filter(StoredFile.folder_id == folder.id)

    return query


def _parse_selected_file_ids() -> list[int]:
    raw_values = request.form.getlist("file_ids")
    if not raw_values:
        raw_csv = request.form.get("file_ids_csv", "")
        raw_values = [value.strip() for value in raw_csv.split(",") if value.strip()]

    selected_ids: list[int] = []
    for raw_value in raw_values:
        try:
            selected_ids.append(int(raw_value))
        except (TypeError, ValueError):
            abort(400)
    return sorted(set(selected_ids))


@bp.post("/files/export")
@login_required
def export_files_csv():
    """Export metadata only for active files owned by the current user.

    VIEWER shares are deliberately excluded because the app only grants viewers
    view/download permissions, not bulk export permissions.
    """
    import csv
    import io
    from datetime import datetime, timezone

    selected_ids = _parse_selected_file_ids()
    query = StoredFile.query.filter(
        StoredFile.owner_id == g.current_user.id,
        StoredFile.is_deleted.is_(False),
    )
    if selected_ids:
        query = query.filter(StoredFile.id.in_(selected_ids))
    else:
        query = _apply_export_filters(query)

    files = query.order_by(StoredFile.id.asc()).all()

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "file_id",
            "original_name",
            "extension",
            "mime_type",
            "size_bytes",
            "folder",
            "owner_username",
            "created_at",
            "updated_at",
        ]
    )
    for stored_file in files:
        writer.writerow(
            [
                stored_file.id,
                stored_file.original_name,
                stored_file.file_extension,
                stored_file.mime_type,
                stored_file.file_size,
                stored_file.folder.name if stored_file.folder else "My Drive",
                stored_file.owner.username,
                stored_file.created_at.isoformat(),
                stored_file.updated_at.isoformat(),
            ]
        )

    from app.models import ExportJob, ExportJobItem

    job = ExportJob(
        requested_by_user=g.current_user,
        export_type="CSV",
        status="COMPLETED",
        item_count=len(files),
        total_size=sum(stored_file.file_size or 0 for stored_file in files),
        completed_at=datetime.now(timezone.utc),
    )
    db.session.add(job)
    db.session.flush()
    for stored_file in files:
        db.session.add(ExportJobItem(export_job=job, file=stored_file))
    db.session.commit()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"studydrive_metadata_{timestamp}.csv"
    csv_text = "\ufeff" + output.getvalue()
    response = current_app.response_class(
        csv_text,
        mimetype="text/csv; charset=utf-8",
    )
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"
    response.headers["X-Export-Job-Id"] = str(job.id)
    return response
