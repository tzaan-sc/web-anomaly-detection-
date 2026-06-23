"""Structured request log model used by the anomaly-detection pipeline."""

from datetime import datetime, timezone

from app.extensions import db


# Thời gian UTC để log đồng nhất giữa các máy chủ.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RequestLog(db.Model):
    # Bảng lưu từng request để phục vụ phân tích bất thường.
    __tablename__ = "request_logs"
    __table_args__ = (
        # Tìm nhanh theo user và thời gian.
        db.Index("ix_request_logs_user_timestamp", "user_id", "timestamp"),
        # Tìm nhanh theo session và thời gian.
        db.Index("ix_request_logs_session_timestamp", "session_id_hash", "timestamp"),
        # Tìm nhanh theo action và thời gian.
        db.Index("ix_request_logs_action_timestamp", "action", "timestamp"),
        # Tìm nhanh theo status code và thời gian.
        db.Index("ix_request_logs_status_timestamp", "status_code", "timestamp"),
        # Tìm nhanh theo loại tài nguyên và id tài nguyên.
        db.Index("ix_request_logs_resource", "resource_type", "resource_id"),
        # Tìm nhanh theo kết quả phân quyền và thời gian.
        db.Index("ix_request_logs_auth_result", "authorization_result", "timestamp"),
    )

    # Mã định danh riêng cho mỗi request.
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    # Thời điểm request xảy ra.
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, index=True)
    # User liên quan đến request, có thể không có.
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Vai trò của user tại thời điểm request.
    role = db.Column(db.String(20), nullable=True)
    # Mã hash của session để theo dõi phiên làm việc.
    session_id_hash = db.Column(db.String(128), nullable=True, index=True)
    # Thông tin mạng và trình duyệt.
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    # Request đang dùng method nào và đi tới endpoint nào.
    http_method = db.Column(db.String(10), nullable=False, index=True)
    endpoint = db.Column(db.String(255), nullable=True, index=True)
    # URL path không gồm query string để tránh lưu dữ liệu nhạy cảm từ tham số.
    path = db.Column(db.String(1024), nullable=True)
    # Hành động nghiệp vụ của request.
    action = db.Column(db.String(80), nullable=True, index=True)
    # Loại tài nguyên và id tài nguyên bị tác động.
    resource_type = db.Column(db.String(50), nullable=True, index=True)
    resource_id = db.Column(db.String(100), nullable=True, index=True)
    # Ai là chủ sở hữu tài nguyên và quyền của request.
    owner_id = db.Column(db.Integer, nullable=True, index=True)
    permission = db.Column(db.String(20), nullable=True, index=True)
    # Kết quả phân quyền: allowed hay denied.
    authorization_result = db.Column(db.String(20), nullable=True, index=True)
    # HTTP status trả về cho request.
    status_code = db.Column(db.Integer, nullable=False, index=True)
    # Thời gian xử lý request tính bằng mili giây.
    response_time_ms = db.Column(db.Float, nullable=False, default=0.0)
    # Thông tin phụ cho nghiệp vụ file/export.
    file_size = db.Column(db.BigInteger, nullable=True)
    export_item_count = db.Column(db.Integer, nullable=True)
    export_total_size = db.Column(db.BigInteger, nullable=True)

    # Nối request log với user.
    user = db.relationship("User", back_populates="request_logs")

    def __repr__(self) -> str:
        return (
            f"<RequestLog request_id={self.request_id!r} action={self.action!r} "
            f"status={self.status_code}>"
        )
