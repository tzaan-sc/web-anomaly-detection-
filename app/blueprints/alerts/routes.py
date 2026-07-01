from __future__ import annotations

import json
from datetime import datetime

from flask import abort, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from app.blueprints.alerts import bp
from app.decorators.authorization import admin_required
from app.extensions import db
from app.models import Alert, RequestLog, User
from app.services.detection_service import alert_log_filter_url_args, run_detection


def _parse_datetime(raw_value: str | None):
    value = (raw_value or "").strip()
    if not value:
        return None
    try:
        if len(value) == 10:
            return datetime.fromisoformat(value)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        abort(400)


def _filter_values() -> dict[str, str]:
    return {
        "start": request.args.get("start", "", type=str).strip()[:40],
        "end": request.args.get("end", "", type=str).strip()[:40],
        "user": request.args.get("user", "", type=str).strip()[:255],
        "hint": request.args.get("hint", "", type=str).strip()[:80],
        "model_version": request.args.get("model_version", "", type=str).strip()[:80],
        "status": request.args.get("status", "", type=str).strip()[:30],
        "sort": request.args.get("sort", "score_desc", type=str).strip()[:30],
    }


def _apply_filters(query, filters: dict[str, str]):
    start_dt = _parse_datetime(filters["start"])
    end_dt = _parse_datetime(filters["end"])
    if start_dt is not None:
        query = query.filter(Alert.window_start >= start_dt)
    if end_dt is not None:
        query = query.filter(Alert.window_end <= end_dt)

    if filters["user"]:
        user_value = filters["user"]
        if user_value.isdigit():
            query = query.filter(Alert.user_id == int(user_value))
        else:
            escaped = user_value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            query = query.outerjoin(User, Alert.user_id == User.id).filter(
                func.lower(User.username).like(f"%{escaped.lower()}%", escape="\\")
                | func.lower(User.email).like(f"%{escaped.lower()}%", escape="\\")
            )
    if filters["hint"]:
        query = query.filter(Alert.scenario_hint == filters["hint"])
    if filters["model_version"]:
        query = query.filter(Alert.model_version == filters["model_version"])
    if filters["status"]:
        query = query.filter(Alert.status == filters["status"])
    return query


def _ordered_query(filters: dict[str, str]):
    query = _apply_filters(Alert.query, filters)
    sort = filters.get("sort") or "score_desc"
    if sort == "oldest":
        return query.order_by(Alert.window_start.asc(), Alert.id.asc())
    if sort == "newest":
        return query.order_by(Alert.window_start.desc(), Alert.id.desc())
    if sort == "score_asc":
        return query.order_by(Alert.anomaly_score.asc(), Alert.id.desc())
    filters["sort"] = "score_desc"
    return query.order_by(Alert.anomaly_score.desc(), Alert.window_start.desc(), Alert.id.desc())


def _loads_features(features_json: str | None) -> dict[str, object]:
    if not features_json:
        return {}
    try:
        return json.loads(features_json)
    except Exception:
        return {"raw": features_json}


@bp.get("/")
@admin_required
def index():
    filters = _filter_values()
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 10), 100)

    pagination = _ordered_query(filters).paginate(page=page, per_page=per_page, error_out=False)

    base_args = request.args.to_dict(flat=True)
    base_args.pop("page", None)

    def page_url(page_number: int) -> str:
        return url_for("alerts.index", **base_args, page=page_number)

    total_logs = RequestLog.query.count()
    total_alerts = Alert.query.count()
    new_alerts = Alert.query.filter_by(status="NEW").count()
    top_users = (
        db.session.query(Alert.user_id, User.username, func.count(Alert.id).label("alert_count"))
        .outerjoin(User, Alert.user_id == User.id)
        .group_by(Alert.user_id, User.username)
        .order_by(func.count(Alert.id).desc())
        .limit(5)
        .all()
    )
    hint_counts = (
        db.session.query(Alert.scenario_hint, func.count(Alert.id).label("count"))
        .group_by(Alert.scenario_hint)
        .order_by(func.count(Alert.id).desc())
        .all()
    )
    hint_options = [row[0] for row in hint_counts if row[0]]
    model_options = [
        row[0]
        for row in db.session.query(Alert.model_version).distinct().order_by(Alert.model_version.asc()).all()
        if row[0]
    ]

    return render_template(
        "alerts/index.html",
        alerts=pagination.items,
        pagination=pagination,
        filters=filters,
        per_page=per_page,
        page_url=page_url,
        total_logs=total_logs,
        total_alerts=total_alerts,
        new_alerts=new_alerts,
        top_users=top_users,
        hint_counts=hint_counts,
        hint_options=hint_options,
        model_options=model_options,
        sort_options=[
            ("score_desc", "Score cao nhất"),
            ("score_asc", "Score thấp nhất"),
            ("newest", "Mới nhất"),
            ("oldest", "Cũ nhất"),
        ],
    )


@bp.post("/run-detection")
@admin_required
def run_detection_action():
    start = _parse_datetime(request.form.get("start"))
    end = _parse_datetime(request.form.get("end"))
    result = run_detection(start=start, end=end)
    category = "success" if result.ok else "warning"
    flash(
        f"{result.message} Windows={result.windows_scored}, anomalies={result.anomalies_found}, "
        f"created={result.alerts_created}, duplicate={result.alerts_skipped_duplicate}.",
        category,
    )
    return redirect(url_for("alerts.index"))


@bp.get("/<int:alert_id>")
@admin_required
def detail(alert_id: int):
    alert = db.session.get(Alert, alert_id)
    if alert is None:
        abort(404)
    feature_payload = _loads_features(alert.features_json)
    log_args = alert_log_filter_url_args(alert)
    related_logs = []
    if alert.window_start and alert.window_end:
        query = RequestLog.query.filter(
            RequestLog.timestamp >= alert.window_start,
            RequestLog.timestamp <= alert.window_end,
        )
        if alert.user_id:
            query = query.filter(RequestLog.user_id == alert.user_id)
        related_logs = query.order_by(RequestLog.timestamp.asc()).limit(100).all()

    return render_template(
        "alerts/detail.html",
        alert=alert,
        feature_payload=feature_payload,
        related_logs=related_logs,
        log_filter_url=url_for("admin.logs", **log_args),
    )
