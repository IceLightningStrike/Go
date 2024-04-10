from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ChangeAbout(FlaskForm):
    new_about = TextAreaField('О себе', validators=[DataRequired()])
    submit = SubmitField('Изменить')