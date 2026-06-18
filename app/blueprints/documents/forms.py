"""WTForms used by the StudyDrive file and folder screens."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class CreateFolderForm(FlaskForm):
    name = StringField(
        "Tên thư mục",
        validators=[
            DataRequired(message="Vui lòng nhập tên thư mục."),
            Length(max=255, message="Tên thư mục tối đa 255 ký tự."),
            Regexp(
                r"^[^/\\]+$",
                message="Tên thư mục không được chứa dấu / hoặc \\\\.",
            ),
        ],
    )
    parent_id = SelectField("Thư mục cha", coerce=int, choices=[])
    submit = SubmitField("Tạo thư mục")


class UploadFileForm(FlaskForm):
    file = FileField(
        "Chọn tệp",
        validators=[FileRequired(message="Vui lòng chọn một tệp để upload.")],
    )
    folder_id = SelectField("Lưu vào", coerce=int, choices=[])
    submit = SubmitField("Upload tệp")
