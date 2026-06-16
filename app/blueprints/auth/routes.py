from flask import (
    flash,
    g,
    redirect,
    render_template,
    session,
    url_for,
)

from app.blueprints.auth import bp
from app.blueprints.auth.forms import (
    ChangePasswordForm,
    LoginForm,
    ProfileForm,
)
from app.decorators.authorization import login_required
from app.extensions import db
from app.models import User
from app.services.auth_service import (
    authenticate_user,
    create_session_hash,
)


def redirect_after_login():
    """Chuyển hướng theo role sau khi đăng nhập."""

    if g.current_user and g.current_user.is_admin:
        return redirect(url_for("admin.index"))

    return redirect(url_for("main.dashboard"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.current_user is not None:
        return redirect_after_login()

    form = LoginForm()

    if form.validate_on_submit():
        user = authenticate_user(
            identifier=form.identifier.data,
            password=form.password.data,
        )

        # Dùng cùng một thông báo cho sai username, sai password
        # và tài khoản bị khóa.
        if user is None:
            flash(
                "Thông tin đăng nhập không hợp lệ hoặc tài khoản không hoạt động.",
                "danger",
            )
            return render_template(
                "auth/login.html",
                form=form,
            )

        # Xóa session cũ để chống session fixation.
        session.clear()

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role
        session["session_id_hash"] = create_session_hash()

        flash("Đăng nhập thành công.", "success")

        if user.is_admin:
            return redirect(url_for("admin.index"))

        return redirect(url_for("main.dashboard"))

    return render_template(
        "auth/login.html",
        form=form,
    )


@bp.post("/logout")
@login_required
def logout():
    session.clear()

    flash("Đã đăng xuất.", "success")

    return redirect(url_for("auth.login"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=g.current_user)

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        username_owner = User.query.filter(
            User.username == username,
            User.id != g.current_user.id,
        ).first()

        if username_owner is not None:
            form.username.errors.append(
                "Tên đăng nhập đã được sử dụng."
            )

        email_owner = User.query.filter(
            User.email == email,
            User.id != g.current_user.id,
        ).first()

        if email_owner is not None:
            form.email.errors.append(
                "Email đã được sử dụng."
            )

        if not form.username.errors and not form.email.errors:
            g.current_user.username = username
            g.current_user.email = email

            db.session.commit()

            session["username"] = username

            flash(
                "Cập nhật hồ sơ thành công.",
                "success",
            )

            return redirect(url_for("auth.profile"))

    return render_template(
        "auth/profile.html",
        form=form,
    )


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not g.current_user.check_password(
            form.old_password.data
        ):
            form.old_password.errors.append(
                "Mật khẩu hiện tại không đúng."
            )
        else:
            g.current_user.set_password(
                form.new_password.data
            )

            db.session.commit()

            # Buộc session hiện tại hết hiệu lực.
            session.clear()

            flash(
                "Đổi mật khẩu thành công. Vui lòng đăng nhập lại.",
                "success",
            )

            return redirect(url_for("auth.login"))

    return render_template(
        "auth/change_password.html",
        form=form,
    )