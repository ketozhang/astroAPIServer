import functools
import requests
from pathlib import Path
import flask
from flask import (
    Flask,
    abort,
    make_response,
    jsonify,
    redirect,
    render_template,
    url_for,
)
from astroapiserver import ENV
from flask_wtf.csrf import generate_csrf, validate_csrf, ValidationError

PROJECT_PATH = Path(__file__).parents[1].resolve()
API_URL = "http://127.0.0.1:8081"

app = Flask(__name__, template_folder=str(PROJECT_PATH / "test" / "templates"))
app.secret_key = ENV["SECRET"]


@app.context_processor
def global_var():
    var = {"API_URL": API_URL, "csrf_token": generate_csrf}
    return var


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        response = requests.get(API_URL, cookies=flask.request.cookies)
        if response.json() and response.json().get("username"):
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


################
# WEB / ROUTES #
################
@app.route("/")
def home():
    context = {}

    response = requests.get(API_URL, cookies=flask.request.cookies)
    if response.json() is not None:
        user_info = response.json()
        context["username"] = user_info.get("username")

    return render_template("home.html", **context)


@app.route("/secret")
@login_required
def secret():
    return jsonify("42")


if __name__ == "__main__":
    app.run(port=8080, debug=True)
