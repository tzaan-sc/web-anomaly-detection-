"""Anomaly alert model."""

from datetime import datetime, timezone

from app.extensions import db


# Lấy thời gian hiện tại theo UTC để lưu thống nhất trong database.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(db.Model):
    # Bảng lưu các cảnh báo bất thường.
    __tablename__ = "alerts"
    __table_args__ = (
        # Không cho tạo 2 cảnh báo trùng window và model version.
        db.UniqueConstraint("window_id", "model_version", name="uq_alert_window_model"),
        # Tạo index để truy vấn nhanh theo user và trạng thái.
        db.Index("ix_alerts_user_status", "user_id", "status"),
        # Tạo index để lọc cảnh báo theo scenario và thời gian tạo.
        db.Index("ix_alerts_scenario_created", "scenario_hint", "created_at"),
    )

    # Thông tin định danh cảnh báo.
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Cửa sổ thời gian mà model dùng để phát hiện.
    window_id = db.Column(db.String(128), nullable=False, index=True)
    window_start = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    window_end = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    # Phiên bản model đã tạo ra cảnh báo này.
    model_version = db.Column(db.String(80), nullable=False, index=True)
    # Điểm bất thường càng cao thì càng đáng nghi.
    anomaly_score = db.Column(db.Float, nullable=False)
    # Gợi ý kịch bản tấn công hoặc hành vi nghi vấn.
    scenario_hint = db.Column(db.String(80), nullable=True, index=True)
    # Lưu các feature dưới dạng JSON.
    features_json = db.Column(db.Text, nullable=False, default="{}")
    # Trạng thái xử lý của cảnh báo.
    status = db.Column(db.String(30), nullable=False, default="NEW", index=True)
    # Ghi chú của Admin khi xử lý.
    admin_notes = db.Column(db.Text, nullable=True)
    # Thời gian tạo và cập nhật.
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Nối cảnh báo với người dùng liên quan.
    user = db.relationship("User", back_populates="alerts")

    def __repr__(self) -> str:
        return (
            f"<Alert id={self.id} scenario={self.scenario_hint!r} "
            f"score={self.anomaly_score}>"
        )
