from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class GameJoin(FlaskForm):
    size_board = StringField('Номер комнаты', validators=[DataRequired()])
    submit = SubmitField('Присоединиться')