from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture()
def app(tmp_path: Path):
    app = create_app("testing")
    app.config.update(
        UPLOAD_FOLDER=str(tmp_path / "uploads"),
        MAX_CONTENT_LENGTH=20 * 1024 * 1024,
    )

    with app.app_context():
        db.create_all()

        admin = User(username="admin", email="admin@test.local", role="ADMIN")
        admin.set_password("AdminPass123!")
        user_a = User(username="user_a", email="a@test.local", role="USER")
        user_a.set_password("UserPass123!")
        user_b = User(username="user_b", email="b@test.local", role="USER")
        user_b.set_password("UserPass123!")
        db.session.add_all([admin, user_a, user_b])
        db.session.commit()

        app.config["TEST_ADMIN_ID"] = admin.id
        app.config["TEST_USER_A_ID"] = user_a.id
        app.config["TEST_USER_B_ID"] = user_b.id

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login_as(client, app):
    def _login(user_id: int):
        with client.session_transaction() as session:
            session.clear()
            session["user_id"] = user_id
            session["session_id_hash"] = "test-session"
        return user_id

    return _login
