"""User account model."""

from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


# Dùng UTC để mọi mốc thời gian giống nhau.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(db.Model):
    # Bảng tài khoản người dùng.
    __tablename__ = "users"

    # Thông tin đăng nhập và vai trò.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    # Mật khẩu đã hash, không lưu mật khẩu thô.
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="USER", index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Các dữ liệu do user sở hữu.
    folders = db.relationship(
        "Folder", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )
    files = db.relationship(
        "StoredFile", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )
    shares_received = db.relationship(
        "FileShare",
        foreign_keys="FileShare.shared_with_user_id",
        back_populates="shared_with_user",
        cascade="all, delete-orphan",
    )
    shares_created = db.relationship(
        "FileShare",
        foreign_keys="FileShare.shared_by_user_id",
        back_populates="shared_by_user",
        cascade="all, delete-orphan",
    )
    # Các job export, log request và alert liên quan đến user.
    export_jobs = db.relationship(
        "ExportJob", back_populates="requested_by_user", cascade="all, delete-orphan"
    )
    request_logs = db.relationship("RequestLog", back_populates="user")
    alerts = db.relationship("Alert", back_populates="user")

    def set_password(self, password: str) -> None:
        # Không cho lưu mật khẩu rỗng.
        if not password:
            raise ValueError("Mật khẩu không được để trống.")
        # Hash mật khẩu trước khi lưu vào database.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        # Nếu thiếu dữ liệu thì coi như sai mật khẩu.
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        # Role ADMIN được xem là quản trị viên.
        return self.role.upper() == "ADMIN"

    def __repr__(self) -> str:
        return f"<User {self.username!r} role={self.role!r}>"
