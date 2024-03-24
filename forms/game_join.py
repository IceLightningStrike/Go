from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class CreateGame(FlaskForm):
    size_board = StringField('Размер поля', validators=[DataRequired()])
    submit = SubmitField('Создать')