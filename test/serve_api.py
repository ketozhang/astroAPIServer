import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).parents[1].resolve()

from flask import (
    Flask,
    abort,
    make_response,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from astroapiserver import API, get_payload, create_auth, login_required, ENV


def authenticate(username, password):
    """
    Use by API by storing payload to user's cookie. Returns cookie (a dict).
    """
    if username != "test" or password != "test":
        return False
    else:
        payload = {"username": username}
        return payload


app = Flask(__name__, template_folder=str(PROJECT_PATH / 'test' / "templates"))
app.secret_key = ENV['SECRET']
api = API(app, authenticate)

################
# WEB / ROUTES #
################
@app.route("/")
def home():
    context = {}

    payload = get_payload()
    if payload is not None:
        context["username"] = payload["username"]
        return context["username"]
    else:
        return 'This page requires login.'
    # return render_template('home.html', **context)


@app.route("/secret")
@login_required
def secret():
    return "42"


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        response = api.login(
            request.form.get("username"), request.form.get("password")
        )

        if response is False:
            print(f"BAD: {response}")
            abort(401)
        else:
            print(f"GOOD: {response}")
            return response


@app.route("/logout", methods=["POST"])
def logout():
    response = api.logout()
    return response


if __name__ == "__main__":
    app.run(port=8081, debug=True)
