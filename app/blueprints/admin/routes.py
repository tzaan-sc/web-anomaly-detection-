from flask import render_template

from app.blueprints.admin import bp


@bp.get("/")
def index():
    return render_template("admin/index.html")
