from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from app.extensions import db
from app.models import ExportJob, FileShare, Folder, StoredFile, User


def _make_physical_file(app, owner: User, name: str, *, deleted: bool = False):
    stored_name = f"stored-{owner.id}-{name}"
    physical_path = Path(app.config["UPLOAD_FOLDER"]) / str(owner.id) / stored_name
    physical_path.parent.mkdir(parents=True, exist_ok=True)
    content = f"content for {name}".encode()
    physical_path.write_bytes(content)
    stored_file = StoredFile(
        original_name=name,
        stored_name=stored_name,
        storage_path=physical_path.as_posix(),
        mime_type="text/plain",
        file_extension="txt",
        file_size=len(content),
        owner=owner,
        is_deleted=deleted,
    )
    db.session.add(stored_file)
    db.session.commit()
    return stored_file


def _csv_rows(response):
    text = response.data.decode("utf-8-sig")
    return list(csv.DictReader(StringIO(text)))


def test_export_csv_has_bom_disposition_and_excludes_foreign_or_deleted_files(
    app, client, login_as
):
    with app.app_context():
        user_a = db.session.get(User, app.config["TEST_USER_A_ID"])
        user_b = db.session.get(User, app.config["TEST_USER_B_ID"])
        own = _make_physical_file(app, user_a, "own.txt")
        deleted = _make_physical_file(app, user_a, "deleted.txt", deleted=True)
        foreign = _make_physical_file(app, user_b, "foreign.txt")
        own_id, deleted_id, foreign_id = own.id, deleted.id, foreign.id

    login_as(app.config["TEST_USER_A_ID"])
    response = client.post(
        "/files/export",
        data={"file_ids": [str(own_id), str(deleted_id), str(foreign_id)]},
    )

    assert response.status_code == 200
    assert response.data.startswith(b"\xef\xbb\xbf")
    assert "attachment" in response.headers["Content-Disposition"]
    assert "studydrive_metadata_" in response.headers["Content-Disposition"]

    rows = _csv_rows(response)
    assert [row["original_name"] for row in rows] == ["own.txt"]
    assert "storage_path" not in rows[0]
    assert "stored_name" not in rows[0]

    with app.app_context():
        job = ExportJob.query.one()
        assert job.status == "COMPLETED"
        assert job.item_count == 1


def test_ten_consecutive_exports_create_ten_jobs(app, client, login_as):
    with app.app_context():
        user_a = db.session.get(User, app.config["TEST_USER_A_ID"])
        stored_file = _make_physical_file(app, user_a, "repeat.txt")
        file_id = stored_file.id

    login_as(app.config["TEST_USER_A_ID"])
    for _ in range(10):
        response = client.post("/files/export", data={"file_ids": [str(file_id)]})
        assert response.status_code == 200
        assert _csv_rows(response)[0]["original_name"] == "repeat.txt"

    with app.app_context():
        assert ExportJob.query.count() == 10


def test_soft_delete_trash_restore_and_viewer_loses_access(app, client, login_as):
    with app.app_context():
        owner = db.session.get(User, app.config["TEST_USER_A_ID"])
        viewer = db.session.get(User, app.config["TEST_USER_B_ID"])
        stored_file = _make_physical_file(app, owner, "trash-me.txt")
        db.session.add(
            FileShare(
                file=stored_file,
                shared_with_user=viewer,
                shared_by_user=owner,
                permission="VIEWER",
            )
        )
        db.session.commit()
        file_id = stored_file.id

    login_as(app.config["TEST_USER_A_ID"])
    delete_response = client.post(f"/files/{file_id}/delete", follow_redirects=False)
    assert delete_response.status_code == 302
    assert "trash-me.txt" in client.get("/trash").get_data(as_text=True)
    assert client.get(f"/files/{file_id}").status_code == 404

    login_as(app.config["TEST_USER_B_ID"])
    assert client.get(f"/files/{file_id}").status_code == 404
    assert "trash-me.txt" not in client.get("/shared-with-me").get_data(as_text=True)

    login_as(app.config["TEST_USER_A_ID"])
    restore_response = client.post(f"/files/{file_id}/restore", follow_redirects=False)
    assert restore_response.status_code == 302
    assert "trash-me.txt" not in client.get("/trash").get_data(as_text=True)
    assert client.get(f"/files/{file_id}").status_code == 200


def test_admin_users_and_metadata_are_admin_only_and_can_lock_user(
    app, client, login_as
):
    with app.app_context():
        user_a = db.session.get(User, app.config["TEST_USER_A_ID"])
        folder = Folder(name="Admin visible", owner=user_a)
        db.session.add(folder)
        db.session.flush()
        stored_file = _make_physical_file(app, user_a, "admin-visible.txt")
        stored_file.folder = folder
        db.session.commit()
        user_a_id = user_a.id

    login_as(app.config["TEST_USER_A_ID"])
    assert client.get("/admin/users").status_code == 403
    assert client.get("/admin/files").status_code == 403

    login_as(app.config["TEST_ADMIN_ID"])
    users_page = client.get("/admin/users?q=user_a")
    assert users_page.status_code == 200
    assert "user_a" in users_page.get_data(as_text=True)

    files_page = client.get("/admin/files?owner=user_a&extension=txt&deleted=active")
    files_text = files_page.get_data(as_text=True)
    assert files_page.status_code == 200
    assert "admin-visible.txt" in files_text
    assert "/download" not in files_text

    folders_page = client.get("/admin/folders?owner=user_a&deleted=active")
    assert folders_page.status_code == 200
    assert "Admin visible" in folders_page.get_data(as_text=True)

    toggle = client.post(f"/admin/users/{user_a_id}/toggle-active", follow_redirects=False)
    assert toggle.status_code == 302
    with app.app_context():
        assert db.session.get(User, user_a_id).is_active is False
