from flask import render_template

from app.blueprints.admin import bp
from app.decorators.authorization import admin_required


@bp.get("/")
@admin_required
def index():
    return render_template("admin/index.html")