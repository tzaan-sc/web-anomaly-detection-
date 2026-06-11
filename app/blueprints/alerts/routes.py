from flask import render_template

from app.blueprints.alerts import bp


@bp.get("/")
def index():
    return render_template("alerts/index.html")
