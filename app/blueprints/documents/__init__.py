from flask import Blueprint

bp = Blueprint("documents", __name__)

from app.blueprints.documents import routes  # noqa: E402, F401
