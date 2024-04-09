from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ChangeAccount(FlaskForm):
    submit = SubmitField('Изменить')