from flask import render_template
from werkzeug.exceptions import HTTPException


def forbidden(error: HTTPException):
    return render_template("errors/403.html", error=error), 403


def page_not_found(error: HTTPException):
    return render_template("errors/404.html", error=error), 404


def server_error(error: Exception):
    return render_template("errors/500.html", error=error), 500