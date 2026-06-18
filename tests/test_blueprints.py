def test_expected_blueprints_are_registered(app):
    expected = {"main", "auth", "documents", "admin", "alerts"}
    assert expected.issubset(app.blueprints.keys())


def test_public_and_protected_routes_are_reachable(client):
    assert client.get("/auth/login").status_code == 200

    protected_paths = ["/files", "/documents/", "/admin/", "/alerts/"]
    for path in protected_paths:
        response = client.get(path)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]
