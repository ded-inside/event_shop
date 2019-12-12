from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password1 = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Password again", validators=[DataRequired()])

    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])

    email = StringField("Email", validators=[DataRequired(), Email()])

    submit = SubmitField("Sign Up")


class UserEditForm(FlaskForm):
    first_name = StringField("First name", validators=[])
    last_name = StringField("Last name", validators=[])

    job = StringField("Job")
    about = TextAreaField("About")

    profile_picture = FileField("Profile picture")

    submit = SubmitField("Update")
