from flask import Flask, render_template, jsonify
from go import Go

app = Flask(__name__)
go = Go(9)

@app.route("/")
def greeting() -> str:
    return render_template("greeting.html")


@app.route('/trigger_function', methods=['POST'])
def trigger_function():
    # TODO: Ваши действия здесь, например, подсчет налоговой декларации 😉
    return jsonify(result='Выполнено')


@app.route("/game")
def game_field() -> str:
    return render_template("game.html", list_html=go.board)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
