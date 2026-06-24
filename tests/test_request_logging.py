from __future__ import annotations

from app.extensions import db
from app.models import RequestLog, StoredFile


def latest_request_log():
    return RequestLog.query.order_by(RequestLog.id.desc()).first()


def create_test_file(owner_id: int, *, name: str = "demo.txt") -> StoredFile:
    stored_file = StoredFile(
        original_name=name,
        stored_name=f"stored-{owner_id}-{name}",
        storage_path=f"uploads/{owner_id}/stored-{owner_id}-{name}",
        mime_type="text/plain",
        file_extension="txt",
        file_size=123,
        owner_id=owner_id,
    )
    db.session.add(stored_file)
    db.session.commit()
    return stored_file


def test_every_handled_request_creates_structured_log(client, app):
    with app.app_context():
        before = RequestLog.query.count()

    response = client.get("/health", headers={"User-Agent": "pytest-agent"})

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")

    with app.app_context():
        assert RequestLog.query.count() == before + 1
        log = latest_request_log()
        assert log.request_id == response.headers["X-Request-ID"]
        assert log.http_method == "GET"
        assert log.path == "/health"
        assert log.endpoint == "main.health"
        assert log.action == "health"
        assert log.action_type == "other"
        assert log.is_authenticated is False
        assert log.is_sensitive is False
        assert log.status_code == 200
        assert log.response_time_ms >= 0
        assert log.user_agent == "pytest-agent"


def test_failed_login_does_not_log_password_or_form_body(client, app):
    response = client.post(
        "/auth/login",
        data={
            "identifier": "user_a",
            "password": "SuperSecretPassword123!",
            "csrf_token": "fake-csrf-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 200
    with app.app_context():
        log = latest_request_log()
        assert log.endpoint == "auth.login"
        assert log.action == "login"
        assert log.action_type == "login"
        assert log.user_id is None
        assert log.is_authenticated is False
        assert log.path == "/auth/login"

        values = [
            log.request_id,
            log.role,
            log.session_id_hash,
            log.ip_address,
            log.user_agent,
            log.http_method,
            log.endpoint,
            log.path,
            log.action,
            log.action_type,
            log.resource_type,
            log.resource_id,
            log.permission,
            log.ownership_result,
            log.authorization_result,
        ]
        joined = " ".join(str(value) for value in values if value is not None)
        assert "SuperSecretPassword123!" not in joined
        assert "fake-csrf-token" not in joined


def test_logging_failure_does_not_break_response(client, monkeypatch):
    def broken_save_request_log(response, response_time_ms):
        raise RuntimeError("simulated logging database failure")

    monkeypatch.setattr(
        "app.middleware.request_logging.save_request_log",
        broken_save_request_log,
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_file_detail_log_has_resource_and_owner_context(client, app, login_as):
    with app.app_context():
        owner_id = app.config["TEST_USER_A_ID"]
        stored_file = create_test_file(owner_id)
        file_id = stored_file.id

    login_as(owner_id)
    response = client.get(f"/files/{file_id}")

    assert response.status_code == 200
    with app.app_context():
        log = latest_request_log()
        assert log.endpoint == "documents.file_detail"
        assert log.action == "view_file_detail"
        assert log.action_type == "view_detail"
        assert log.resource_type == "file"
        assert log.resource_id == str(file_id)
        assert log.owner_id == owner_id
        assert log.permission == "OWNER"
        assert log.ownership_result == "OWNER"
        assert log.authorization_result == "allowed"
        assert log.is_authenticated is True
        assert log.is_sensitive is False
        assert log.file_size == 123


def test_unauthorized_file_detail_is_sensitive_and_has_none_context(client, app, login_as):
    with app.app_context():
        owner_id = app.config["TEST_USER_A_ID"]
        other_user_id = app.config["TEST_USER_B_ID"]
        stored_file = create_test_file(owner_id, name="private.txt")
        file_id = stored_file.id

    login_as(other_user_id)
    response = client.get(f"/files/{file_id}")

    assert response.status_code == 404
    with app.app_context():
        log = latest_request_log()
        assert log.action_type == "view_detail"
        assert log.resource_type == "file"
        assert log.resource_id == str(file_id)
        assert log.owner_id == owner_id
        assert log.permission == "NONE"
        assert log.ownership_result == "NONE"
        assert log.authorization_result == "denied"
        assert log.is_sensitive is True


def test_delete_log_has_delete_action_type_and_sensitive_context(client, app, login_as):
    with app.app_context():
        owner_id = app.config["TEST_USER_A_ID"]
        stored_file = create_test_file(owner_id, name="delete-me.txt")
        file_id = stored_file.id

    login_as(owner_id)
    response = client.post(f"/files/{file_id}/delete")

    assert response.status_code == 302
    with app.app_context():
        log = latest_request_log()
        assert log.endpoint == "documents.delete_file"
        assert log.action == "delete_file"
        assert log.action_type == "delete"
        assert log.resource_type == "file"
        assert log.resource_id == str(file_id)
        assert log.ownership_result == "OWNER"
        assert log.is_sensitive is True
