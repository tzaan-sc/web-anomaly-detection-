"""Authorization decorators."""

from functools import wraps

from flask import abort, flash, g, redirect, url_for


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if g.current_user is None:
            flash(
                "Vui lòng đăng nhập để tiếp tục.",
                "warning",
            )
            return redirect(url_for("auth.login"))

        return view_function(*args, **kwargs)

    return wrapped_view


def admin_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if g.current_user is None:
            flash(
                "Vui lòng đăng nhập để tiếp tục.",
                "warning",
            )
            return redirect(url_for("auth.login"))

        if not g.current_user.is_admin:
            abort(403)

        return view_function(*args, **kwargs)

    return wrapped_view