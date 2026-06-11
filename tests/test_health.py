def test_health_returns_200(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_home_uses_base_layout(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"StudyDrive" in response.data
    assert b"/auth/login" in response.data


def test_admin_navbar_is_role_aware(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "Admin Demo"
        session["role"] = "admin"

    response = client.get("/")

    assert response.status_code == 200
    assert b"/admin/" in response.data
    assert b"/alerts/" in response.data


def test_custom_404(client):
    response = client.get("/duong-dan-khong-ton-tai")

    assert response.status_code == 404
    assert b"404" in response.data
