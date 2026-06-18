"""WTForms used by the StudyDrive file and folder screens."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


_SAFE_NAME_VALIDATORS = [
    DataRequired(message="Vui lòng nhập tên."),
    Length(max=255, message="Tên tối đa 255 ký tự."),
    Regexp(r"^[^/\\]+$", message="Tên không được chứa dấu / hoặc \\."),
]


class CreateFolderForm(FlaskForm):
    name = StringField("Tên thư mục", validators=_SAFE_NAME_VALIDATORS)
    parent_id = SelectField("Thư mục cha", coerce=int, choices=[])
    submit = SubmitField("Tạo thư mục")


class UploadFileForm(FlaskForm):
    file = FileField(
        "Chọn tệp",
        validators=[FileRequired(message="Vui lòng chọn một tệp để upload.")],
    )
    folder_id = SelectField("Lưu vào", coerce=int, choices=[])
    submit = SubmitField("Upload tệp")


class RenameFileForm(FlaskForm):
    original_name = StringField("Tên tệp mới", validators=_SAFE_NAME_VALIDATORS)
    submit = SubmitField("Lưu tên mới")


class MoveFileForm(FlaskForm):
    folder_id = SelectField("Di chuyển đến", coerce=int, choices=[])
    submit = SubmitField("Di chuyển")


class ShareFileForm(FlaskForm):
    recipient_id = SelectField("Người nhận", coerce=int, choices=[])
    submit = SubmitField("Chia sẻ quyền VIEWER")
