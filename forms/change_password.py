from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ChangePassword(FlaskForm):
    new_password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить')