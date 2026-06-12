from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Optional
)


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")


class WordForm(FlaskForm):
    english = StringField(
        "English Word",
        validators=[DataRequired(), Length(min=1, max=100)]
    )

    russian = StringField(
        "Russian Translation",
        validators=[DataRequired(), Length(min=1, max=100)]
    )

    example_sentence = StringField(
        "Example Sentence",
        validators=[Length(max=300)]
    )

    submit = SubmitField("Save Word")


class AccountForm(FlaskForm):
    username = StringField(
        "New Username",
        validators=[DataRequired(), Length(min=3, max=80)]
    )

    email = StringField(
        "New Email",
        validators=[DataRequired(), Email()]
    )

    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired()]
    )

    new_password = PasswordField(
        "New Password",
        validators=[Optional(), Length(min=6)]
    )

    submit = SubmitField("Update Account")


class UploadForm(FlaskForm):
    file = FileField("Upload File", validators=[DataRequired()])
    submit = SubmitField("Upload")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(min=2, max=80)])
    submit = SubmitField("Save Category")