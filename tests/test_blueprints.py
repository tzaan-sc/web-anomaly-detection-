def test_expected_blueprints_are_registered(app):
    expected = {"main", "auth", "documents", "admin", "alerts"}

    assert expected.issubset(app.blueprints.keys())


def test_module_routes_are_reachable(client):
    paths = ["/auth/login", "/documents/", "/admin/", "/alerts/"]

    for path in paths:
        response = client.get(path)
        assert response.status_code == 200
