from flask import Blueprint

bp = Blueprint("alerts", __name__)

from app.blueprints.alerts import routes  # noqa: E402, F401
