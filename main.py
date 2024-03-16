from flask import Flask, render_template, request, redirect, make_response
from settings import HOST, PORT, COUNT_OF_PLAY_FUNCTIONS

from field_picture_drawing import update_board_picture
from preparing import *
from go import Go

from flask import Flask, render_template, redirect, request, make_response, session
from data import db_session
from data.users import User
from data.news import News
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user
from forms.login_form import LoginForm
from forms.register_form import RegisterForm

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init('db/blogs.db')
db_sess = db_session.create_session()

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def creat_similar_game_functions() -> None:
    for play_number in range(1, COUNT_OF_PLAY_FUNCTIONS + 1):
        with open("game_function_pattern.txt", "r", encoding="UTF-8") as file:
            exec(file.read().format(*((play_number,) * 7)))


@app.route("/")
def greeting() -> str:
    return render_template("greeting.html")


@app.route('/trigger_function', methods=['POST'])
def trigger_function():
    if request.method == 'POST':
        game_numbrer = int(request.form["game_number"])
        ip_address = request.access_route[-1]

        first, second = [
            (
                    ip_address == games_dictionary[game_numbrer]["player_1"] and
                    games_dictionary[game_numbrer]["game"].turn == "black"
            ),
            (
                    ip_address == games_dictionary[game_numbrer]["player_2"] and
                    games_dictionary[game_numbrer]["game"].turn == "white"
            )
        ]

        if not (first or second):
            return "Error"

        site_field_width, site_field_height = map(int, map(float, request.form["size"].split(";")))

        field_width = site_field_width // (games_dictionary[game_numbrer]["game"].width + 3)
        field_height = site_field_height // (games_dictionary[game_numbrer]["game"].height + 3)

        x, y = map(int, map(float, request.form["coordinates"].split(";")))
        x, y = x - field_width * 2, y - field_height * 2
        x, y = (x + field_width // 2) // field_width, (y + field_height // 2) // field_height

        try:
            games_dictionary[game_numbrer]["game"].move(
                f"{games_dictionary[game_numbrer]['game'].height - y}" +
                f"{games_dictionary[game_numbrer]['game'].alphabet[x]}"
            )
            update_board_picture(game_numbrer, games_dictionary[game_numbrer]["game"])
        except Exception as error:
            print(repr(error))

        return "Ok"
    return "Error"


@app.route("/game")
def game_field() -> str:
    ip_address = request.access_route[-1]

    for key in range(1, COUNT_OF_PLAY_FUNCTIONS + 1):
        if games_dictionary[key] is None:
            games_dictionary[key] = {
                "game": Go(9),
                "player_1": ip_address,
                "player_2": None
            }
            update_board_picture(key, games_dictionary[key]["game"])
            return redirect(f"game/{key}")

    return render_template("no_memory_for_fields_error.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == "__main__":
    creat_similar_game_functions()
    app.run(host=HOST, port=PORT)
