from flask import flash, redirect, render_template, session, url_for

from app.blueprints.auth import bp


@bp.get("/login")
def login():
    return render_template("auth/login.html")


@bp.post("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất.", "success")
    return redirect(url_for("main.index"))
