from datetime import UTC, datetime

from flask import jsonify, render_template

from app.blueprints.main import bp


@bp.get("/")
def index():
    return render_template("main/index.html")


@bp.get("/health")
def health():
    return (
        jsonify(
            status="ok",
            service="studydrive",
            timestamp=datetime.now(UTC).isoformat(),
        ),
        200,
    )
