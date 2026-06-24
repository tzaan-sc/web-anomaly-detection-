from __future__ import annotations

from app.models import RequestLog


def test_admin_can_filter_logs_and_open_detail(client, app, login_as):
    client.get("/health", headers={"User-Agent": "admin-log-test"})
    with app.app_context():
        health_log = RequestLog.query.filter_by(path="/health").order_by(RequestLog.id.desc()).first()
        assert health_log is not None
        log_id = health_log.id

    login_as(app.config["TEST_ADMIN_ID"])
    response = client.get("/admin/logs?path_keyword=/health&status_code=200&sort=newest")

    assert response.status_code == 200
    assert b"/health" in response.data
    assert b"Request logs" in response.data

    detail = client.get(f"/admin/logs/{log_id}")
    assert detail.status_code == 200
    assert b"admin-log-test" in detail.data
    assert b"Request ID" in detail.data


def test_admin_logs_export_csv_uses_current_filter(client, app, login_as):
    client.get("/health")
    login_as(app.config["TEST_ADMIN_ID"])

    response = client.get("/admin/logs/export?path_keyword=/health")

    assert response.status_code == 200
    assert response.mimetype.startswith("text/csv")
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert b"request_id" in response.data
    assert b"/health" in response.data


def test_regular_user_is_blocked_from_admin_logs(client, app, login_as):
    login_as(app.config["TEST_USER_A_ID"])

    response = client.get("/admin/logs")

    assert response.status_code == 403
