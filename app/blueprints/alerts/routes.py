from flask import render_template

from app.blueprints.alerts import bp
from app.decorators.authorization import admin_required


@bp.get("/")
@admin_required
def index():
    return render_template("alerts/index.html")