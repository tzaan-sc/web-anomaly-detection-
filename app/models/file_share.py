"""Per-file sharing model."""

from datetime import datetime, timezone

from app.extensions import db


# Lấy giờ UTC để lưu share time thống nhất.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FileShare(db.Model):
    # Bảng lưu thông tin chia sẻ file.
    __tablename__ = "file_shares"
    __table_args__ = (
        # Một file không nên share trùng cho cùng một người.
        db.UniqueConstraint(
            "file_id", "shared_with_user_id", name="uq_file_shares_file_recipient"
        ),
        # Tìm share nhanh theo người nhận và quyền.
        db.Index("ix_file_shares_recipient_permission", "shared_with_user_id", "permission"),
        # Tìm share theo file và thời điểm thu hồi.
        db.Index("ix_file_shares_file_revoked", "file_id", "revoked_at"),
    )

    # Thông tin share cốt lõi.
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(
        db.Integer, db.ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Người được nhận file.
    shared_with_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Quyền truy cập, mặc định là viewer.
    permission = db.Column(db.String(20), nullable=False, default="VIEWER")
    # Người đã chia sẻ file này.
    shared_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Nối tới file gốc.
    file = db.relationship("StoredFile", back_populates="shares")
    # Nối tới user nhận share.
    shared_with_user = db.relationship(
        "User", foreign_keys=[shared_with_user_id], back_populates="shares_received"
    )
    # Nối tới user tạo share.
    shared_by_user = db.relationship(
        "User", foreign_keys=[shared_by_user_id], back_populates="shares_created"
    )

    @property
    def is_active(self) -> bool:
        # Chưa bị revoke thì vẫn còn hiệu lực.
        return self.revoked_at is None

    def __repr__(self) -> str:
        return (
            f"<FileShare file_id={self.file_id} recipient={self.shared_with_user_id} "
            f"permission={self.permission!r}>"
        )
