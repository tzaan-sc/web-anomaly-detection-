"""Forms for authentication and profile."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    Regexp,
)


class LoginForm(FlaskForm):
    identifier = StringField(
        "Tên đăng nhập hoặc email",
        validators=[
            DataRequired(message="Vui lòng nhập tên đăng nhập hoặc email."),
            Length(max=255),
        ],
    )

    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu."),
        ],
    )

    submit = SubmitField("Đăng nhập")


class ProfileForm(FlaskForm):
    username = StringField(
        "Tên đăng nhập",
        validators=[
            DataRequired(message="Tên đăng nhập không được để trống."),
            Length(min=3, max=80),
            Regexp(
                r"^[A-Za-z0-9_.-]+$",
                message="Tên đăng nhập chỉ được chứa chữ, số, dấu chấm, gạch dưới và gạch ngang.",
            ),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email không được để trống."),
            Length(max=255),
            Regexp(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                message="Email không đúng định dạng.",
            ),
        ],
    )

    submit = SubmitField("Lưu thay đổi")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "Mật khẩu hiện tại",
        validators=[DataRequired(message="Vui lòng nhập mật khẩu hiện tại.")],
    )

    new_password = PasswordField(
        "Mật khẩu mới",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu mới."),
            Length(
                min=8,
                max=128,
                message="Mật khẩu mới phải có ít nhất 8 ký tự.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Xác nhận mật khẩu mới",
        validators=[
            DataRequired(message="Vui lòng xác nhận mật khẩu mới."),
            EqualTo(
                "new_password",
                message="Mật khẩu xác nhận không khớp.",
            ),
        ],
    )

    submit = SubmitField("Đổi mật khẩu")