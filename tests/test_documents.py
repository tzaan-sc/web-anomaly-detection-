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


def _make_physical_file(app, owner: User, name: str, *, folder: Folder | None = None):
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
        folder=folder,
    )
    db.session.add(stored_file)
    db.session.commit()
    return stored_file, content, physical_path


def test_owner_view_download_and_api_hide_storage_metadata(app, client, login_as):
    with app.app_context():
        owner = db.session.get(User, app.config["TEST_USER_A_ID"])
        stored_file, content, _path = _make_physical_file(app, owner, "owner.txt")
        file_id = stored_file.id

    login_as(app.config["TEST_USER_A_ID"])

    detail = client.get(f"/files/{file_id}")
    assert detail.status_code == 200
    text = detail.get_data(as_text=True)
    assert "OWNER" in text
    assert "Đổi tên" in text
    assert "Chia sẻ" in text

    download = client.get(f"/files/{file_id}/download")
    assert download.status_code == 200
    assert download.data == content
    assert "attachment" in download.headers["Content-Disposition"]
    assert "owner.txt" in download.headers["Content-Disposition"]

    api = client.get(f"/api/files/{file_id}")
    assert api.status_code == 200
    payload = api.get_json()
    assert payload["access"] == "OWNER"
    assert payload["original_name"] == "owner.txt"
    assert "storage_path" not in payload
    assert "stored_name" not in payload


def test_viewer_can_only_view_and_download_while_none_gets_same_404(
    app, client, login_as
):
    from app.models import FileShare

    with app.app_context():
        owner = db.session.get(User, app.config["TEST_USER_A_ID"])
        viewer = db.session.get(User, app.config["TEST_USER_B_ID"])
        stored_file, content, _path = _make_physical_file(app, owner, "shared.txt")
        share = FileShare(
            file=stored_file,
            shared_with_user=viewer,
            shared_by_user=owner,
            permission="VIEWER",
        )
        db.session.add(share)
        outsider = User(username="outsider", email="outside@test.local", role="USER")
        outsider.set_password("UserPass123!")
        db.session.add(outsider)
        db.session.commit()
        file_id = stored_file.id
        outsider_id = outsider.id

    login_as(app.config["TEST_USER_B_ID"])
    detail = client.get(f"/files/{file_id}")
    assert detail.status_code == 200
    text = detail.get_data(as_text=True)
    assert "VIEWER" in text
    assert "Đổi tên" not in text
    assert client.get(f"/files/{file_id}/download").data == content
    api_payload = client.get(f"/api/files/{file_id}").get_json()
    assert api_payload["access"] == "VIEWER"
    assert "folder" not in api_payload

    assert client.get(f"/files/{file_id}/rename").status_code == 404
    assert client.post(
        f"/files/{file_id}/move", data={"folder_id": "0"}
    ).status_code == 404
    assert client.get(f"/files/{file_id}/share").status_code == 404

    login_as(outsider_id)
    assert client.get(f"/files/{file_id}").status_code == 404
    assert client.get(f"/files/{file_id}/download").status_code == 404
    denied_api = client.get(f"/api/files/{file_id}")
    missing_api = client.get("/api/files/999999")
    assert denied_api.status_code == missing_api.status_code == 404
    assert denied_api.get_json() == missing_api.get_json() == {"error": "file_not_found"}


def test_missing_physical_file_returns_404_without_accepting_client_path(
    app, client, login_as
):
    with app.app_context():
        owner = db.session.get(User, app.config["TEST_USER_A_ID"])
        stored_file, _content, physical_path = _make_physical_file(
            app, owner, "missing.txt"
        )
        file_id = stored_file.id
        physical_path.unlink()

    login_as(app.config["TEST_USER_A_ID"])
    assert client.get(f"/files/{file_id}").status_code == 200
    assert client.get(f"/files/{file_id}/download").status_code == 404
    assert client.get(f"/files/{file_id}/download?path=/etc/passwd").status_code == 404


def test_owner_rename_keeps_uuid_and_move_rejects_foreign_folder(
    app, client, login_as
):
    with app.app_context():
        owner = db.session.get(User, app.config["TEST_USER_A_ID"])
        other = db.session.get(User, app.config["TEST_USER_B_ID"])
        own_folder = Folder(name="Own target", owner=owner)
        foreign_folder = Folder(name="Foreign target", owner=other)
        db.session.add_all([own_folder, foreign_folder])
        db.session.flush()
        stored_file, _content, _path = _make_physical_file(
            app, owner, "before.txt"
        )
        file_id = stored_file.id
        old_stored_name = stored_file.stored_name
        old_storage_path = stored_file.storage_path
        own_folder_id = own_folder.id
        foreign_folder_id = foreign_folder.id

    login_as(app.config["TEST_USER_A_ID"])
    rename = client.post(
        f"/files/{file_id}/rename",
        data={"original_name": "after.txt"},
        follow_redirects=False,
    )
    assert rename.status_code == 302

    with app.app_context():
        stored_file = db.session.get(StoredFile, file_id)
        assert stored_file.original_name == "after.txt"
        assert stored_file.stored_name == old_stored_name
        assert stored_file.storage_path == old_storage_path

    bad_extension = client.post(
        f"/files/{file_id}/rename", data={"original_name": "after.pdf"}
    )
    assert bad_extension.status_code == 200
    assert "giữ nguyên phần mở rộng" in bad_extension.get_data(as_text=True)

    move = client.post(
        f"/files/{file_id}/move",
        data={"folder_id": str(own_folder_id)},
        follow_redirects=False,
    )
    assert move.status_code == 302
    with app.app_context():
        assert db.session.get(StoredFile, file_id).folder_id == own_folder_id

    blocked = client.post(
        f"/files/{file_id}/move", data={"folder_id": str(foreign_folder_id)}
    )
    assert blocked.status_code == 404
    with app.app_context():
        assert db.session.get(StoredFile, file_id).folder_id == own_folder_id


def test_share_duplicate_revoke_and_shared_with_me_access_changes_immediately(
    app, client, login_as
):
    from app.models import FileShare

    with app.app_context():
        owner = db.session.get(User, app.config["TEST_USER_A_ID"])
        stored_file, _content, _path = _make_physical_file(app, owner, "grant.txt")
        file_id = stored_file.id
        viewer_id = app.config["TEST_USER_B_ID"]

    login_as(app.config["TEST_USER_A_ID"])
    share_response = client.post(
        f"/files/{file_id}/share",
        data={"recipient_id": str(viewer_id)},
        follow_redirects=False,
    )
    assert share_response.status_code == 302

    duplicate = client.post(
        f"/files/{file_id}/share", data={"recipient_id": str(viewer_id)}
    )
    assert duplicate.status_code == 200
    assert "đã được chia sẻ" in duplicate.get_data(as_text=True)

    self_share = client.post(
        f"/files/{file_id}/share",
        data={"recipient_id": str(app.config["TEST_USER_A_ID"])},
    )
    assert self_share.status_code == 200
    with app.app_context():
        assert FileShare.query.filter_by(file_id=file_id).count() == 1
        share_id = FileShare.query.filter_by(file_id=file_id).one().id

    login_as(viewer_id)
    shared_page = client.get("/shared-with-me")
    assert shared_page.status_code == 200
    assert "grant.txt" in shared_page.get_data(as_text=True)
    assert client.get(f"/files/{file_id}").status_code == 200

    login_as(app.config["TEST_USER_A_ID"])
    revoke = client.post(
        f"/files/{file_id}/shares/{share_id}/revoke", follow_redirects=False
    )
    assert revoke.status_code == 302

    login_as(viewer_id)
    assert "grant.txt" not in client.get("/shared-with-me").get_data(as_text=True)
    assert client.get(f"/files/{file_id}").status_code == 404
    assert client.get(f"/files/{file_id}/download").status_code == 404

    # Re-sharing restores the existing row instead of violating the unique key.
    login_as(app.config["TEST_USER_A_ID"])
    restored = client.post(
        f"/files/{file_id}/share",
        data={"recipient_id": str(viewer_id)},
        follow_redirects=False,
    )
    assert restored.status_code == 302
    with app.app_context():
        shares = FileShare.query.filter_by(file_id=file_id).all()
        assert len(shares) == 1
        assert shares[0].revoked_at is None


def test_deleted_file_is_inaccessible_to_owner_and_viewer(app, client, login_as):
    from app.models import FileShare

    with app.app_context():
        owner = db.session.get(User, app.config["TEST_USER_A_ID"])
        viewer = db.session.get(User, app.config["TEST_USER_B_ID"])
        stored_file, _content, _path = _make_physical_file(app, owner, "deleted.txt")
        db.session.add(
            FileShare(
                file=stored_file,
                shared_with_user=viewer,
                shared_by_user=owner,
                permission="VIEWER",
            )
        )
        stored_file.is_deleted = True
        db.session.commit()
        file_id = stored_file.id

    login_as(app.config["TEST_USER_A_ID"])
    assert client.get(f"/files/{file_id}").status_code == 404
    login_as(app.config["TEST_USER_B_ID"])
    assert client.get(f"/files/{file_id}").status_code == 404
    assert "deleted.txt" not in client.get("/shared-with-me").get_data(as_text=True)
