import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).parents[1].resolve()
sys.path.insert(0, str(PROJECT_PATH))

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
from astroapiserver import API, get_payload, create_auth, login_required


def authenticate(username, password):
    """
    Use by API by storing payload to user's cookie. Returns cookie (a dict).
    """
    if username != "test" or password != "test":
        abort(401)
    else:
        payload = {"username": username}
        return payload


app = Flask(__name__, template_folder=str(PROJECT_PATH / "templates"))
app.secret_key = "test"
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

    return render_template("home.html", **context)


@app.route("/secret")
@login_required
def secret():
    return "42"


@app.route("/login", methods=["POST"])
def login():
    response = api.login(
        request.form.get("username"), request.form.get("password")
    )

    if response is False:
        abort(401)
    else:
        return response


@app.route("/logout", methods=["POST"])
def logout():
    response = api.logout()
    return response


if __name__ == "__main__":
    app.run(port=8080, debug=True)
