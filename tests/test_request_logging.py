from __future__ import annotations

from app.models import RequestLog


def latest_request_log():
    return RequestLog.query.order_by(RequestLog.id.desc()).first()


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
        assert log.user_id is None
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
            log.resource_type,
            log.resource_id,
            log.permission,
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
