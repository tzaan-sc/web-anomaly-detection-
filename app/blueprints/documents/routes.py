from flask import render_template

from app.blueprints.documents import bp
from app.decorators.authorization import login_required


@bp.get("/")
@login_required
def index():
    return render_template("documents/index.html")