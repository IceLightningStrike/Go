from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def greeting() -> str:
    return render_template("greeting.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
