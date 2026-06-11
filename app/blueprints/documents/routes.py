from flask import render_template

from app.blueprints.documents import bp


@bp.get("/")
def index():
    return render_template("documents/index.html")
