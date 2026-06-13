"""Stored file metadata model."""

from datetime import datetime, timezone

from app.extensions import db


# Giờ UTC dùng cho các mốc thời gian của file.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StoredFile(db.Model):
    # Bảng lưu metadata của file đã upload.
    __tablename__ = "files"
    __table_args__ = (
        # Tìm file nhanh theo owner và folder.
        db.Index("ix_files_owner_folder", "owner_id", "folder_id"),
        # Tìm file nhanh theo owner và trạng thái xóa.
        db.Index("ix_files_owner_deleted", "owner_id", "is_deleted"),
        # Tìm file theo thời gian tạo.
        db.Index("ix_files_created_at", "created_at"),
    )

    # Thông tin nhận diện file.
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(255), nullable=False)
    # Tên file lưu trên server, thường là duy nhất.
    stored_name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    # Đường dẫn thực trên ổ đĩa.
    storage_path = db.Column(db.String(1024), nullable=False, unique=True)
    # Kiểu nội dung và phần đuôi file.
    mime_type = db.Column(db.String(255), nullable=False)
    file_extension = db.Column(db.String(20), nullable=False, index=True)
    # Dung lượng file.
    file_size = db.Column(db.BigInteger, nullable=False, default=0)
    # Người sở hữu file.
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Folder chứa file, có thể để trống.
    folder_id = db.Column(
        db.Integer, db.ForeignKey("folders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Xóa mềm.
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Nối file với user sở hữu.
    owner = db.relationship("User", back_populates="files")
    # Nối file với folder chứa nó.
    folder = db.relationship("Folder", back_populates="files")
    # Các lần chia sẻ của file này.
    shares = db.relationship(
        "FileShare", back_populates="file", cascade="all, delete-orphan"
    )
    # Các item export chứa file này.
    export_items = db.relationship(
        "ExportJobItem", back_populates="file", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<StoredFile id={self.id} original_name={self.original_name!r} "
            f"owner_id={self.owner_id}>"
        )
