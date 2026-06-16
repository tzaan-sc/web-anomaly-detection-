"""Authentication services."""

import hashlib
import secrets

from sqlalchemy import func, or_

from app.models import User


def find_user_by_identifier(identifier: str) -> User | None:
    """Tìm user bằng username hoặc email, không phân biệt hoa thường."""

    normalized = identifier.strip().lower()

    return User.query.filter(
        or_(
            func.lower(User.username) == normalized,
            func.lower(User.email) == normalized,
        )
    ).first()


def authenticate_user(identifier: str, password: str) -> User | None:
    """Kiểm tra tài khoản, mật khẩu và trạng thái hoạt động."""

    user = find_user_by_identifier(identifier)

    if user is None:
        return None

    if not user.is_active:
        return None

    if not user.check_password(password):
        return None

    return user


def create_session_hash() -> str:
    """Tạo fingerprint cho session và chỉ trả về bản hash."""

    raw_value = secrets.token_urlsafe(32)

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()