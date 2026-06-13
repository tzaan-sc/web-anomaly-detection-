"""Logical folder model for StudyDrive."""

from datetime import datetime, timezone

from app.extensions import db


# Lấy giờ UTC để thống nhất thời gian trong hệ thống.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Folder(db.Model):
    # Bảng lưu thư mục logic.
    __tablename__ = "folders"
    __table_args__ = (
        # Tìm thư mục nhanh theo owner và thư mục cha.
        db.Index("ix_folders_owner_parent", "owner_id", "parent_id"),
        # Tìm thư mục nhanh theo owner và trạng thái xóa mềm.
        db.Index("ix_folders_owner_deleted", "owner_id", "is_deleted"),
    )

    # Thông tin cơ bản của folder.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # Người sở hữu folder.
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Folder cha để tạo cây thư mục.
    parent_id = db.Column(
        db.Integer, db.ForeignKey("folders.id", ondelete="CASCADE"), nullable=True, index=True
    )
    # Xóa mềm thay vì xóa hẳn.
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Nối folder với user sở hữu.
    owner = db.relationship("User", back_populates="folders")
    # Quan hệ cha-con để tạo cấu trúc cây.
    parent = db.relationship(
        "Folder", remote_side=[id], back_populates="children", foreign_keys=[parent_id]
    )
    # Danh sách folder con.
    children = db.relationship(
        "Folder", back_populates="parent", cascade="all, delete-orphan", single_parent=True
    )
    # Các file nằm trong folder này.
    files = db.relationship("StoredFile", back_populates="folder")

    def __repr__(self) -> str:
        return f"<Folder id={self.id} name={self.name!r} owner_id={self.owner_id}>"
