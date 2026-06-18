"""Routes for StudyDrive folders, safe uploads, and My Files browsing."""

from __future__ import annotations

from flask import (
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

from app.blueprints.documents import bp
from app.blueprints.documents.forms import CreateFolderForm, UploadFileForm
from app.decorators.authorization import login_required
from app.models import Folder, StoredFile
from app.services.document_service import (
    DocumentValidationError,
    active_folder_choices,
    create_folder as create_folder_record,
    folder_breadcrumb,
    format_file_size,
    get_owned_folder,
    save_uploaded_file,
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
        # Returning 404 avoids confirming that another user's folder exists.
        abort(404)
    return folder


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
        parent = submitted_parent

        try:
            folder = create_folder_record(
                owner=g.current_user,
                name=form.name.data,
                parent=parent,
            )
        except DocumentValidationError as exc:
            form.name.errors.append(str(exc))
        except Exception:
            current_app.logger.exception("Không thể tạo thư mục")
            flash("Không thể tạo thư mục. Dữ liệu chưa được lưu.", "danger")
        else:
            flash(f"Đã tạo thư mục “{folder.name}” thành công.", "success")
            if parent is not None:
                return redirect(url_for("documents.browse_folder", folder_id=parent.id))
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
        folder = submitted_folder

        try:
            stored_file = save_uploaded_file(
                file_storage=form.file.data,
                owner=g.current_user,
                folder=folder,
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
            if folder is not None:
                return redirect(url_for("documents.browse_folder", folder_id=folder.id))
            return redirect(url_for("documents.index"))

    return render_template(
        "documents/upload.html",
        form=form,
        max_size_mb=current_app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024),
        allowed_extensions=sorted(current_app.config["ALLOWED_EXTENSIONS"]),
    )
