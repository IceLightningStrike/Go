from settings import HOST, PORT

from flask import Flask, render_template, request, redirect
from flask import Response

from flask_login import LoginManager, login_user

from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from forms.create_game import CreateGame
from forms.del_account import DelAccount
from forms.game_join import GameJoin

from data import db_session
from data.users import User
from data.client import Client

from field_picture_drawing import update_board_picture
from go import Go

from os import mkdir

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init('db/players.db')

client_tuple = {}

games_list = [None]

try:
    mkdir("static/game_links")
except FileExistsError:
    pass


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def greeting() -> str:
    ip_address = request.access_route[-1]
    param = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Главное меню'
    }

    if request.access_route[-1] in client_tuple.keys():
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]

    return render_template("greeting.html", **param)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    ip_address = request.access_route[-1]
    param = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in client_tuple:
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]

    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                template_name_or_list='register.html',
                title='Регистрация',
                form=form,
                message="Пароли не совпадают",
                **param
            )

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                template_name_or_list='register.html',
                title='Регистрация',
                form=form,
                message="Такой пользователь уже есть",
                **param
            )

        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        client_tuple[request.access_route[-1]] = [user.id, user.name, False]

        return redirect("/")

    return render_template(
        template_name_or_list='register.html',
        title='Регистрация',
        form=form,
        **param
    )


@app.route('/login', methods=['GET', 'POST'])
def login() -> str | Response:
    ip_address = request.access_route[-1]

    param = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in client_tuple:
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]

    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user=user, remember=form.remember_me.data)
            client_tuple[request.access_route[-1]] = [user.id, user.name, False]

            return redirect("/")

        return render_template(
            template_name_or_list='login.html',
            message="Неправильный логин или пароль",
            form=form,
            **param
        )

    return render_template(
        template_name_or_list='login.html',
        title='Авторизация',
        form=form,
        **param
    )


@app.route('/out')
def out() -> Response:
    ip_address = request.access_route[-1]

    try:
        del client_tuple[ip_address]
    except KeyError as error:
        print(repr(error))

    return redirect("/")


@app.route('/user_data')
def user_data() -> str:
    ip_address = request.access_route[-1]
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == client_tuple[ip_address][0]).first()
    # count_win
    # count
    user_list = [f"{name}({count})" for (name, count) in sorted(
        [[elem.name, elem.count_win] for elem in db_sess.query(User).all()],
        key=lambda x: x[-1],
        reverse=True
    )
                 ]

    place = user_list.index(f'{user.name}({user.count_win})') + 1
    param = {
        'name_is_exist': False,
        'name': 1,
        "text_me": user.about,
        'title': 'Аккаунт',
        'count_win': user.count_win,
        'count': user.count,
        'user_list': user_list,
        'name_user': f'{user.name}({user.count_win})',
        'place': place
    }

    if ip_address in client_tuple:
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]
        param['play_game'] = True

    return render_template(
        template_name_or_list="data_user.html",
        **param
    )


@app.route("/leader_board")
def leader_board() -> None:
    ip_address = request.access_route[-1]
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == client_tuple[ip_address][0]).first()
    # count_win
    # count
    user_list = [f"{name}({count})" for (name, count) in sorted(
        [[elem.name, elem.count_win] for elem in db_sess.query(User).all()],
        key=lambda x: x[-1],
        reverse=True
    )
                 ]

    place = user_list.index(f'{user.name}({user.count_win})') + 1
    param = {
        'name_is_exist': False,
        'name': 1,
        "text_me": user.about,
        'title': 'Аккаунт',
        'count_win': user.count_win,
        'count': user.count,
        'user_list': user_list,
        'name_user': f'{user.name}({user.count_win})'
    }
    return render_template(
        template_name_or_list="table_leadry.html",
        **param
    )


@app.route("/game_create", methods=['GET', 'POST'])
def game_create() -> str:
    ip_address = request.access_route[-1]
    form = CreateGame()
    param = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Создать комнату',
        'form': form
    }
    if request.access_route[-1] in client_tuple.keys():
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]
    if form.validate_on_submit():
        pass

    return render_template(template_name_or_list="game_create.html", **param)


@app.route('/game_room', methods=['GET', 'POST'])
def game_room():
    ip_address = request.access_route[-1]

    param = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in client_tuple:
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]

    form = GameJoin()

    if form.validate_on_submit():
        if int(form.size_board.data) < len(games_list):
            print(form.size_board.data, len(games_list))

            return redirect(f"/game/{form.size_board.data}")

        return render_template(
            template_name_or_list='game_room.html',
            message="Нет такой комнаты",
            title='Присоединиться к комнате',
            form=form,
            **param
        )

    return render_template(
        template_name_or_list='game_room.html',
        title='Присоединиться к комнате',
        form=form,
        **param
    )


@app.route('/game_callback_answer', methods=['POST'])
def game_callback_answer() -> str:
    if request.method == 'POST':
        game_number = int(request.form["game_number"])
        ip_address = request.access_route[-1]

        first, second = [
            (
                    ip_address == games_list[game_number]["player_1"] and
                    games_list[game_number]["game"].turn == "black"
            ),
            (
                    ip_address == games_list[game_number]["player_2"] and
                    games_list[game_number]["game"].turn == "white"
            )
        ]

        if not (first or second):
            return "Error"

        site_field_width, site_field_height = map(int, map(float, request.form["size"].split(";")))

        field_width = site_field_width // (games_list[game_number]["game"].width + 3)
        field_height = site_field_height // (games_list[game_number]["game"].height + 3)

        x, y = map(int, map(float, request.form["coordinates"].split(";")))
        x, y = x - field_width * 2, y - field_height * 2
        x, y = (x + field_width // 2) // field_width, (y + field_height // 2) // field_height

        try:
            games_list[game_number]["game"].move(
                f"{games_list[game_number]['game'].height - y}" +
                f"{games_list[game_number]['game'].alphabet[x]}"
            )
            update_board_picture(game_number, games_list[game_number]["game"])
        except Exception as error:
            print(repr(error))

        return "Ok"
    return "Error"


@app.route("/game")
def game_field() -> str:
    ip_address = request.access_route[-1]
    game_number = len(games_list)

    try:
        mkdir(f"static/game_links/{game_number}")
    except FileExistsError:
        pass

    games_list.append({
        "game": Go(19),
        "player_1": ip_address,
        "player_2": None
    })

    update_board_picture(game_number, games_list[game_number]["game"])

    return redirect(f"/game/{game_number}")


@app.route("/del", methods=['GET', 'POST'])
def del_account():
    ip_address = request.access_route[-1]

    param = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in client_tuple:
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]

    form = DelAccount()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            db_sess.query(User).filter(User.id == client_tuple[request.access_route[-1]][0]).delete()
            db_sess.commit()
            del client_tuple[request.access_route[-1]]

            return redirect("/")

        return render_template(
            template_name_or_list='del_account.html',
            message="Неправильный логин или пароль(Подтвердите данные)",
            form=form,
            **param
        )

    return render_template(
        template_name_or_list='del_account.html',
        title='Удаление аккаунта!!!',
        form=form,
        message="Подтвердите данные",
        **param
    )


@app.route(f"/game/<int:game_number>")
def basic_game_function(game_number: int) -> str:
    ip_address = request.access_route[-1]

    if not (1 <= game_number <= len(games_list)):
        return render_template(
            "basic_error_messages.html",
            messages=[
                "Game ID is incorrect!"
            ]
        )

    if games_list[game_number]["player_2"] is None:
        if ip_address != games_list[game_number]["player_1"]:
            games_list[game_number]["player_2"] = ip_address

    ip_address = request.access_route[-1]
    id_plays = [games_list[game_number]["player_1"], games_list[game_number]["player_2"]]
    id_plays.pop(id_plays.index(ip_address))
    param = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Go',
        'player_is_exist': True,
        'name_player': None,
        'number_room': game_number
    }

    if request.access_route[-1] in client_tuple.keys():
        param['name_is_exist'] = True
        param['name'] = client_tuple[ip_address][1]

    if not id_plays[0] is None:
        param['player_is_exist'] = True
        param['name_player'] = client_tuple[id_plays[1]]
    # [user.id, user.name, False]

    print(param)
    print(games_list)

    return render_template("game.html", **param)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
