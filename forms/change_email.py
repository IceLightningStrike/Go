from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ChangeEmail(FlaskForm):
    new_email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Изменить')