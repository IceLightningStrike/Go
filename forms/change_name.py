from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ChangeName(FlaskForm):
    new_name = StringField('Новое имя', validators=[DataRequired()])
    submit = SubmitField('Изменить')