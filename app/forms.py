from flask_wtf import FlaskForm
from wtforms import (StringField,
                     PasswordField,
                     BooleanField,
                     SubmitField,
                     TextAreaField,
                     FileField
                     )
from wtforms.fields.html5 import (DateTimeField,
                                  IntegerField,
                                  DateField,
                                  )
from wtforms.validators import (DataRequired,
                                Length,
                                Email,
                                ValidationError,
                                NumberRange,
                                EqualTo,
                                )
from app.models import *


class LoginForm(FlaskForm):
    username = StringField("Username",
                           validators=[
                               DataRequired(message="Поле обязательно для заполнения")])    # noqa
    password = PasswordField("Password",
                             validators=[
                                 DataRequired(message="Поле обязательно для заполнения")])  # noqa
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(message="Поле обязательно для заполнения"),
                    Length(min=4,
                           max=25,
                           message="Длина должна быть от %(min)d до %(max)d символов")])    # noqa
    password1 = PasswordField(
        "Password",
        validators=[DataRequired(
            message="Поле обязательно для заполнения"),
            EqualTo("password2",
                    message="Пароль должен совпадать")])
    password2 = PasswordField("Password again", validators=[
                              DataRequired(message="Поле обязательно для заполнения")])  # noqa

    first_name = StringField("First name", validators=[
                             DataRequired(message="Поле обязательно для заполнения")])  # noqa
    last_name = StringField("Last name", validators=[
                            DataRequired(message="Поле обязательно для заполнения")])  # noqa
    email = StringField("Email",
                        validators=[DataRequired(
                            message="Поле обязательно для заполнения"),
                            Email(message="email введен не корректно"),
                            Length(min=4,
                                   max=35,
                                   message=f"Длина должна быть от {min} до {max} символов")])   # noqa
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста ввидите другой логин.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста ввидите другой email.')


class UserEditForm(FlaskForm):
    first_name = StringField("First name", validators=[])
    last_name = StringField("Last name", validators=[])

    job = StringField("Job")
    about = TextAreaField("About")

    profile_picture = FileField("Profile picture")

    submit = SubmitField("Update")


class EventForm(FlaskForm):
    title = StringField("Title", validators=[
                        DataRequired(
                            message="Поле обязательно для заполнения"),
                        Length(min=3, max=64)])
    about = TextAreaField("About")

    time_start = DateTimeField("Begins", validators=[DataRequired(
        message="Поле обязательно для заполнения")])
    time_end = DateTimeField("Ends", validators=[DataRequired(
        message="Поле обязательно для заполнения")])

    price = IntegerField("Cost", validators=[NumberRange(min=1)])

    submit = SubmitField("Add")
