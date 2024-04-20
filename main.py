from settings import HOST, PORT

from flask import Flask, render_template, request, redirect
from flask import Blueprint, Response

from flask_login import LoginManager, login_user

from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from forms.create_game import CreateGame
from forms.del_account import DelAccount
from forms.game_join import GameJoin
from forms.change_about import ChangeAbout
from forms.change_password import ChangePassword
from forms.change_name import ChangeName

from data import db_session
from data.users import User
from data.client import Client

from field_picture_drawing import update_board_picture, save_game_replay
from go import Go

from os import mkdir

from time import time, sleep

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
blueprint = Blueprint('go_api', __name__, template_folder='templates')

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init('db/players.db')
db_sess = db_session.create_session()

clients_dictionary = dict()
games_list = [None]

try:
    mkdir("static/game_links")
except FileExistsError:
    pass


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route("/")
def greeting() -> str:
    ip_address = request.access_route[-1]
    parametrs = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Главное меню'
    }

    if ip_address in clients_dictionary:
        parametrs['name'] = clients_dictionary[ip_address][1]
        parametrs['name_is_exist'] = True

    return render_template("greeting.html", **parametrs)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    ip_address = request.access_route[-1]
    parametrs = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in clients_dictionary:
        parametrs['name'] = clients_dictionary[ip_address][1]
        parametrs['name_is_exist'] = True

    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                template_name_or_list='register.html',
                title='Регистрация',
                form=form,
                message="Пароли не совпадают",
                **parametrs
            )

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                template_name_or_list='register.html',
                title='Регистрация',
                form=form,
                message="Такой пользователь уже есть",
                **parametrs
            )

        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )

        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        user = db_sess.query(User).filter(User.email == form.email.data).first()
        clients_dictionary[request.access_route[-1]] = [user.id, user.name, False]

        return redirect("/")

    return render_template(
        template_name_or_list='register.html',
        title='Регистрация',
        form=form,
        **parametrs
    )


@app.route('/login', methods=['GET', 'POST'])
def login() -> str | Response:
    ip_address = request.access_route[-1]

    parametrs = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in clients_dictionary:
        parametrs['name_is_exist'] = True
        parametrs['name'] = clients_dictionary[ip_address][1]

    form = LoginForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user=user, remember=form.remember_me.data)
            clients_dictionary[request.access_route[-1]] = [user.id, user.name, False]

            return redirect("/")

        return render_template(
            template_name_or_list='login.html',
            message="Неправильный логин или пароль",
            form=form,
            **parametrs
        )

    return render_template(
        template_name_or_list='login.html',
        title='Авторизация',
        form=form,
        **parametrs
    )


@app.route('/out')
def out() -> Response:
    ip_address = request.access_route[-1]

    try:
        del clients_dictionary[ip_address]
    except KeyError as error:
        print(repr(error))

    return redirect("/")


@app.route('/user_data')
def user_data() -> str:
    ip_address = request.access_route[-1]

    user = db_sess.query(User).filter(User.id == clients_dictionary[ip_address][0]).first()
    user_list = [f"{name}({count})" for (name, count) in sorted(
        [[elem.name, elem.count_win] for elem in db_sess.query(User).all()],
        key=lambda x: x[-1],
        reverse=True
    )
                 ]

    place = user_list.index(f'{user.name}({user.count_win})') + 1
    parametrs = {
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

    if ip_address in clients_dictionary:
        parametrs['name_is_exist'] = True
        parametrs['name'] = clients_dictionary[ip_address][1]
        parametrs['play_game'] = True

    return render_template(
        template_name_or_list="data_user.html",
        **parametrs
    )


@app.route('/change_account')
def change_account():
    ip_address = request.access_route[-1]
    parametrs = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Редактирование Аккаунта'
    }
    if ip_address in clients_dictionary:
        parametrs['name'] = clients_dictionary[ip_address][1]
        parametrs['name_is_exist'] = True
    return render_template('change_account.html', **parametrs)


@app.route('/change_name', methods=['GET', 'POST'])
def change_name():
    ip_address = request.access_route[-1]
    parametrs = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Редактирование имя'
    }

    form = ChangeName()

    if ip_address in clients_dictionary:
        parametrs['name'] = clients_dictionary[ip_address][1]
        parametrs['name_is_exist'] = True
    if form.validate_on_submit():
        data = form.new_name.data
        user = db_sess.query(User).filter(User.id == clients_dictionary[ip_address][0]).first()
        user.name = data
        clients_dictionary[ip_address][1] = data
        db_sess.add(user)
        db_sess.commit()
        return redirect('/user_data')

    return render_template('change_name.html', form=form, **parametrs)


@app.route('/change_about', methods=['GET', 'POST'])
def change_about():
    ip_address = request.access_route[-1]

    parametrs = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Редактирование о себе'
    }

    form = ChangeAbout()

    if ip_address in clients_dictionary:
        parametrs['name'] = clients_dictionary[ip_address][1]
        parametrs['name_is_exist'] = True
    if form.validate_on_submit():
        data = form.new_about.data
        user = db_sess.query(User).filter(User.id == clients_dictionary[ip_address][0]).first()
        user.about = data
        db_sess.add(user)
        db_sess.commit()
        return redirect('/user_data')
    return render_template('change_about.html', form=form, **parametrs)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    ip_address = request.access_route[-1]
    parametrs = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Редактирование пароля'
    }

    form = ChangePassword()

    if ip_address in clients_dictionary:
        parametrs['name'] = clients_dictionary[ip_address][1]
        parametrs['name_is_exist'] = True
    if form.validate_on_submit():
        data = form.new_password.data
        user = db_sess.query(User).filter(User.id == clients_dictionary[ip_address][0]).first()
        user.set_password(data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/user_data')
    return render_template('change_password.html', form=form, **parametrs)


@app.route("/leader_board")
def leader_board() -> None:
    ip_address = request.access_route[-1]

    user = db_sess.query(User).filter(User.id == clients_dictionary[ip_address][0]).first()
    user_list = [f"{name}({count})" for (name, count) in sorted(
        [[elem.name, elem.count_win] for elem in db_sess.query(User).all()],
        key=lambda x: x[-1],
        reverse=True
    )
                 ]

    parametrs = {
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
        **parametrs
    )


@app.route("/game_create", methods=['GET', 'POST'])
def game_create() -> str:
    ip_address = request.access_route[-1]
    game_number = len(games_list)

    games_counter = 0
    for game_information in games_list:
        if game_information is None:
            continue

        try:
            if game_information["player_1"] == ip_address and not game_information["was_closed"]:
                games_counter += 1
        except KeyError:
            pass

        try:
            if game_information["player_2"] == ip_address and not game_information["was_closed"]:
                games_counter += 1
        except KeyError:
            pass

    if games_counter >= 3:
        return render_template("basic_error_messages.html", messages=[
            "You can't start more than 3 games at the same time"
        ])

    form = CreateGame()
    parametrs = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Создать комнату',
        'form': form
    }

    if request.access_route[-1] in clients_dictionary.keys():
        parametrs['name_is_exist'] = True
        parametrs['name'] = clients_dictionary[ip_address][1]

    if form.validate_on_submit():
        list_size = [0, 9, 13, 19]
        size_board = list_size[int(form.size_board.data)]

        list_room = {
            "game": Go(size_board),
            "player_1": None,
            "player_2": None,
            "room_open": form.open_room.data,
            "was_closed": False
        }

        print(form.count_stone.data)
        if int(form.count_stone.data) > 0:
            if size_board == 9:
                if int(form.count_stone.data) > 5:
                    list_room["game"].handicap_stones(5)
                else:
                    list_room["game"].handicap_stones(int(form.count_stone.data))
            else:
                if int(form.count_stone.data) > 9:
                    list_room["game"].handicap_stones(9)
                else:
                    list_room["game"].handicap_stones(int(form.count_stone.data))

        if form.black_white.data == "1":
            list_room['player_1'] = ip_address
        else:
            list_room['player_2'] = ip_address

        games_list.append(list_room)

        try:
            mkdir(f"static/game_links/{game_number}")
        except FileExistsError:
            pass

        update_board_picture(games_list[game_number]["game"], game_number)
        print(games_list)
        return redirect(f"/game/{game_number}")
    return render_template(template_name_or_list="game_create.html", **parametrs)


@app.route("/game_join")
def game_join():
    ip_address = request.access_route[-1]
    for i in range(1, len(games_list)):
        if not games_list[i]['room_open'] and (games_list[i]['player_1'] is None or games_list[i]['player_2'] is None):
            if games_list[i]['player_1'] is None:
                games_list[i]['player_1'] = ip_address
            else:
                games_list[i]['player_2'] = ip_address
            print(games_list)
            return redirect(f"/game/{i}")
    return redirect('/')


@app.route('/game_room', methods=['GET', 'POST'])
def game_room():
    ip_address = request.access_route[-1]

    parametrs = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in clients_dictionary:
        parametrs['name_is_exist'] = True
        parametrs['name'] = clients_dictionary[ip_address][1]

    form = GameJoin()

    if form.validate_on_submit():
        if int(form.size_board.data) < len(games_list):
            print(form.size_board.data, len(games_list))
            if games_list[int(form.size_board.data)]['player_1'] is None:
                games_list[int(form.size_board.data)]['player_1'] = request.access_route[-1]
            if games_list[int(form.size_board.data)]['player_2'] is None:
                games_list[int(form.size_board.data)]['player_2'] = request.access_route[-1]

            return redirect(f"/game/{form.size_board.data}")

        return render_template(
            template_name_or_list='game_room.html',
            message="Нет такой комнаты",
            title='Присоединиться к комнате',
            form=form,
            **parametrs
        )

    return render_template(
        template_name_or_list='game_room.html',
        title='Присоединиться к комнате',
        form=form,
        **parametrs
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
            update_board_picture(games_list[game_number]["game"], game_number)
        except Exception as error:
            print(repr(error))

        return "Ok"
    return "Error"


@app.route("/del", methods=['GET', 'POST'])
def del_account():
    ip_address = request.access_route[-1]

    parametrs = {
        'name_is_exist': False,
        'name': 1
    }

    if ip_address in clients_dictionary:
        parametrs['name_is_exist'] = True
        parametrs['name'] = clients_dictionary[ip_address][1]

    form = DelAccount()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            db_sess.query(User).filter(User.id == clients_dictionary[request.access_route[-1]][0]).delete()
            db_sess.commit()
            del clients_dictionary[request.access_route[-1]]

            return redirect("/")

        return render_template(
            template_name_or_list='del_account.html',
            message="Неправильный логин или пароль(Подтвердите данные)",
            form=form,
            **parametrs
        )

    return render_template(
        template_name_or_list='del_account.html',
        title='Удаление аккаунта!!!',
        form=form,
        message="Подтвердите данные",
        **parametrs
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

    if games_list[game_number]["player_1"] == ip_address:
        opponent_ip = games_list[game_number]["player_2"]
    else:
        opponent_ip = games_list[game_number]["player_1"]

    parametrs = {
        'name_is_exist': False,
        'name': 1,
        'title': 'Go',
        'player_is_exist': True,
        'name_player': None,
        'number_room': game_number
    }

    if request.access_route[-1] in clients_dictionary:
        parametrs['name_is_exist'] = True
        parametrs['name'] = clients_dictionary[ip_address][1]

    if not opponent_ip is None:
        parametrs['player_is_exist'] = True
        parametrs['name_player'] = clients_dictionary[opponent_ip][1]

    return render_template("game.html", **parametrs)


@blueprint.route('/api/game_save/game_id=<int:game_id>/speed=<int:speed>')
def get_go_replay(game_id, speed):
    ip_address = request.access_route[-1]

    try:
        mkdir(f"static/game_links/{game_id}/{ip_address}")
    except Exception:
        pass

    try:
        assert 1 <= speed <= 10

        save_game_replay(games_list[game_id]["game"], game_id, ip_address, speed=speed)
    except Exception as error:
        print(repr(error))
        return render_template("basic_error_messages.html", messages=[
            "Wrong request"
        ])

    return render_template("show_game_api.html", game_id=game_id, ip=ip_address)


if __name__ == "__main__":
    app.register_blueprint(blueprint)
    app.run(host=HOST, port=PORT)
