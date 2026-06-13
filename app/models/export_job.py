"""Export job models."""

from datetime import datetime, timezone

from app.extensions import db


# Thời gian UTC dùng cho các mốc tạo/hoàn tất job.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExportJob(db.Model):
    # Bảng chính lưu một lần export.
    __tablename__ = "export_jobs"
    __table_args__ = (
        # Tìm job nhanh theo người yêu cầu và trạng thái.
        db.Index("ix_export_jobs_user_status", "requested_by_user_id", "status"),
        # Sắp xếp/tìm job theo thời gian tạo.
        db.Index("ix_export_jobs_created_at", "created_at"),
    )

    # Thông tin cơ bản của job export.
    id = db.Column(db.Integer, primary_key=True)
    requested_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Kiểu export, ví dụ CSV.
    export_type = db.Column(db.String(20), nullable=False, default="CSV")
    # Số lượng file trong job.
    item_count = db.Column(db.Integer, nullable=False, default=0)
    # Tổng dung lượng dữ liệu export.
    total_size = db.Column(db.BigInteger, nullable=False, default=0)
    # Trạng thái job.
    status = db.Column(db.String(30), nullable=False, default="PENDING", index=True)
    # Đường dẫn file kết quả export.
    output_path = db.Column(db.String(1024), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Ai là người tạo job.
    requested_by_user = db.relationship("User", back_populates="export_jobs")
    # Danh sách các file nằm trong job.
    items = db.relationship(
        "ExportJobItem", back_populates="export_job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ExportJob id={self.id} status={self.status!r} items={self.item_count}>"


class ExportJobItem(db.Model):
    # Mỗi dòng đại diện cho một file trong job export.
    __tablename__ = "export_job_items"
    __table_args__ = (
        # Một file chỉ xuất hiện 1 lần trong cùng job.
        db.UniqueConstraint(
            "export_job_id", "file_id", name="uq_export_job_items_job_file"
        ),
    )

    # Thông tin liên kết giữa job và file.
    id = db.Column(db.Integer, primary_key=True)
    export_job_id = db.Column(
        db.Integer,
        db.ForeignKey("export_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_id = db.Column(
        db.Integer, db.ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    # Nối về job cha.
    export_job = db.relationship("ExportJob", back_populates="items")
    # Nối về file được export.
    file = db.relationship("StoredFile", back_populates="export_items")

    def __repr__(self) -> str:
        return f"<ExportJobItem job_id={self.export_job_id} file_id={self.file_id}>"
