from __future__ import annotations

from io import BytesIO
from pathlib import Path

from app.extensions import db
from app.models import Folder, StoredFile, User


def _upload(client, filename: str, content: bytes, mime: str, folder_id: int = 0):
    return client.post(
        "/files/upload",
        data={
            "folder_id": str(folder_id),
            "file": (BytesIO(content), filename, mime),
        },
        content_type="multipart/form-data",
        follow_redirects=False,
    )


def test_create_folder_and_upload_valid_file(app, client, login_as):
    login_as(app.config["TEST_USER_A_ID"])

    response = client.post(
        "/folders/create",
        data={"name": "Do an 3", "parent_id": "0"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    with app.app_context():
        folder = Folder.query.filter_by(
            owner_id=app.config["TEST_USER_A_ID"], name="Do an 3"
        ).one()
        folder_id = folder.id

    response = _upload(
        client,
        "bao-cao.txt",
        b"Noi dung bao cao StudyDrive",
        "text/plain",
        folder_id,
    )
    assert response.status_code == 302

    with app.app_context():
        stored_file = StoredFile.query.filter_by(
            owner_id=app.config["TEST_USER_A_ID"],
            original_name="bao-cao.txt",
        ).one()
        assert stored_file.folder_id == folder_id
        assert stored_file.stored_name != stored_file.original_name
        assert stored_file.stored_name.endswith(".txt")
        assert len(Path(stored_file.stored_name).stem) == 32

        physical_path = Path(app.instance_path) / stored_file.storage_path
        assert physical_path.exists()
        assert physical_path.read_bytes() == b"Noi dung bao cao StudyDrive"
        assert physical_path.stat().st_size == stored_file.file_size
        assert Path(app.static_folder) not in physical_path.parents


def test_upload_rejects_too_large_file_without_garbage(app, client, login_as):
    login_as(app.config["TEST_USER_A_ID"])
    app.config["MAX_CONTENT_LENGTH"] = 128

    response = _upload(client, "large.txt", b"x" * 1024, "text/plain")
    assert response.status_code == 413

    with app.app_context():
        assert StoredFile.query.filter_by(original_name="large.txt").count() == 0
    upload_root = Path(app.config["UPLOAD_FOLDER"])
    assert not list(upload_root.rglob("*")) if upload_root.exists() else True


def test_upload_rejects_forbidden_extension(app, client, login_as):
    login_as(app.config["TEST_USER_A_ID"])
    response = _upload(
        client,
        "malware.exe",
        b"MZ-not-allowed",
        "application/x-msdownload",
    )
    assert response.status_code == 200
    assert "Định dạng tệp không được phép" in response.get_data(as_text=True)

    with app.app_context():
        assert StoredFile.query.count() == 0


def test_upload_cannot_target_another_users_folder(app, client, login_as):
    with app.app_context():
        owner_b = db.session.get(User, app.config["TEST_USER_B_ID"])
        foreign_folder = Folder(name="Private B", owner=owner_b)
        db.session.add(foreign_folder)
        db.session.commit()
        foreign_folder_id = foreign_folder.id

    login_as(app.config["TEST_USER_A_ID"])
    response = _upload(
        client,
        "secret.txt",
        b"safe text",
        "text/plain",
        foreign_folder_id,
    )
    assert response.status_code == 404

    with app.app_context():
        assert StoredFile.query.count() == 0


def test_special_filename_is_sanitized_and_cannot_escape_upload_root(
    app, client, login_as
):
    login_as(app.config["TEST_USER_A_ID"])
    response = _upload(
        client,
        "../../bài tập 01.txt",
        b"du lieu hop le",
        "text/plain",
    )
    assert response.status_code == 302

    with app.app_context():
        stored_file = StoredFile.query.one()
        assert stored_file.original_name == "bai_tap_01.txt"
        physical_path = (Path(app.instance_path) / stored_file.storage_path).resolve()
        upload_root = Path(app.config["UPLOAD_FOLDER"]).resolve()
        assert physical_path.is_relative_to(upload_root)
        assert ".." not in stored_file.storage_path
        assert "/" not in stored_file.stored_name
        assert "\\" not in stored_file.stored_name


def test_mime_or_signature_mismatch_is_rejected(app, client, login_as):
    login_as(app.config["TEST_USER_A_ID"])
    response = _upload(
        client,
        "fake.pdf",
        b"This is not a PDF",
        "application/pdf",
    )
    assert response.status_code == 200
    assert "Nội dung tệp không khớp" in response.get_data(as_text=True)
    with app.app_context():
        assert StoredFile.query.count() == 0


def test_database_failure_removes_physical_file(
    app, client, login_as, monkeypatch
):
    login_as(app.config["TEST_USER_A_ID"])

    def fail_commit():
        raise RuntimeError("simulated database failure")

    monkeypatch.setattr(db.session, "commit", fail_commit)
    response = _upload(
        client,
        "rollback.txt",
        b"rollback test",
        "text/plain",
    )
    assert response.status_code == 200
    assert "đã rollback" in response.get_data(as_text=True)

    upload_root = Path(app.config["UPLOAD_FOLDER"])
    files = [path for path in upload_root.rglob("*") if path.is_file()]
    assert files == []


def test_file_list_search_filter_sort_pagination_and_isolation(
    app, client, login_as
):
    with app.app_context():
        user_a = db.session.get(User, app.config["TEST_USER_A_ID"])
        user_b = db.session.get(User, app.config["TEST_USER_B_ID"])
        folder_a = Folder(name="A Folder", owner=user_a)
        folder_b = Folder(name="B Private", owner=user_b)
        db.session.add_all([folder_a, folder_b])
        db.session.flush()

        for index in range(12):
            db.session.add(
                StoredFile(
                    original_name=f"report-{index:02d}.txt",
                    stored_name=f"a-{index:02d}.txt",
                    storage_path=f"uploads/a-{index:02d}.txt",
                    mime_type="text/plain",
                    file_extension="txt",
                    file_size=100 + index,
                    owner=user_a,
                    folder=folder_a,
                )
            )
        db.session.add(
            StoredFile(
                original_name="private-b.txt",
                stored_name="private-b.txt",
                storage_path="uploads/private-b.txt",
                mime_type="text/plain",
                file_extension="txt",
                file_size=999,
                owner=user_b,
                folder=folder_b,
            )
        )
        db.session.commit()
        folder_a_id = folder_a.id
        folder_b_id = folder_b.id

    login_as(app.config["TEST_USER_A_ID"])

    response = client.get("/files?q=report-1&extension=txt&sort=size_desc")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "report-11.txt" in text
    assert "private-b.txt" not in text

    response = client.get("/files?page=2&q=report&extension=txt&sort=name_asc")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "report-10.txt" in text
    assert "q=report" in text
    assert "extension=txt" in text

    response = client.get(f"/folders/{folder_a_id}")
    assert response.status_code == 200
    assert "report-11.txt" in response.get_data(as_text=True)

    response = client.get(f"/folders/{folder_b_id}")
    assert response.status_code == 404


def test_create_folder_rejects_another_users_parent(app, client, login_as):
    with app.app_context():
        user_b = db.session.get(User, app.config["TEST_USER_B_ID"])
        folder_b = Folder(name="Only B", owner=user_b)
        db.session.add(folder_b)
        db.session.commit()
        folder_b_id = folder_b.id

    login_as(app.config["TEST_USER_A_ID"])
    response = client.post(
        "/folders/create",
        data={"name": "Illegal child", "parent_id": str(folder_b_id)},
    )
    assert response.status_code == 404

    with app.app_context():
        assert Folder.query.filter_by(name="Illegal child").count() == 0
