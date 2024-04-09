from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, RadioField, BooleanField
from wtforms.validators import DataRequired


class CreateGame(FlaskForm):
    size_board = RadioField('Размер доски: ', choices=[
        (1, "9X9"),
        (2, "13X13"),
        (3, "19X19"),
    ],
                            default=1,
                            validators=[DataRequired()])
    black_white = RadioField('Цвет фигуры: ', choices=[
        (1, "Черные"),
        (2, "Белые"),
    ],
                             default=2,
                             validators=[DataRequired()])
    open_room = BooleanField('Закрытая комната:')
    submit = SubmitField('Создать')
