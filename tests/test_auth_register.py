from app.models import User
from app.services.auth_service import authenticate_user


def test_register_page_loads(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert "Đăng ký" in response.get_data(as_text=True)


def test_successful_registration(client, app):
    response = client.post(
        "/auth/register",
        data={
            "username": "newstudent",
            "email": "newstudent@test.local",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Đăng ký tài khoản thành công" in response.get_data(as_text=True)

    with app.app_context():
        user = User.query.filter_by(username="newstudent").first()
        assert user is not None
        assert user.email == "newstudent@test.local"
        assert user.role == "USER"
        assert user.is_active is True
        assert user.check_password("Password123!") is True


def test_registration_existing_username(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "user_a",
            "email": "brandnew@test.local",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )

    assert response.status_code == 200
    assert "Tên đăng nhập đã được sử dụng." in response.get_data(as_text=True)


def test_registration_existing_email(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "unique_user",
            "email": "a@test.local",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )

    assert response.status_code == 200
    assert "Email đã được sử dụng." in response.get_data(as_text=True)


def test_registration_password_mismatch(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "anotheruser",
            "email": "another@test.local",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!",
        },
    )

    assert response.status_code == 200
    assert "Mật khẩu xác nhận không khớp." in response.get_data(as_text=True)


def test_registered_user_can_login(client, app):
    client.post(
        "/auth/register",
        data={
            "username": "testloginuser",
            "email": "testlogin@test.local",
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!",
        },
        follow_redirects=True,
    )

    with app.app_context():
        user = authenticate_user("testloginuser", "ValidPassword123!")
        assert user is not None
        assert user.username == "testloginuser"
