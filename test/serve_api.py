import sys
from pathlib import Path
import logging
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

PROJECT_PATH = Path(__file__).parents[1].resolve()
from astroapiserver import API, create_auth, ENV


def authenticate(username, password):
    """
    Use by API by storing payload to user's cookie. Returns cookie (a dict).
    """
    if username != "test" or password != "test":
        return False
    else:
        payload = {"username": username}
        return payload


app = Flask(__name__, template_folder=str(PROJECT_PATH / "test" / "templates"))
app.secret_key = ENV["SECRET"]
logging.basicConfig(level=logging.DEBUG)
logger = app.logger
api = API(app, authenticate)

################
# WEB / ROUTES #
################
@app.route("/")
def home():
    user_info = api.get_user_info()
    if user_info is not None:
        return jsonify(user_info)
    else:
        return jsonify(None)


@app.route("/secret")
@api.login_required
def secret():
    return "42"


@app.route("/login", methods=["POST"])
def login():
    username, password = (
        request.form.get("username"),
        request.form.get("password"),
    )
    logger.info(f"Login Requested for <{username}> ...")
    response = api.login(username, password)

    if response is False:
        logger.info("Login Failed")
        abort(401)
    else:
        logger.info("Login Success")
        return response


@app.route("/logout", methods=["POST"])
def logout():
    logger.info("Logout Requested...")
    response = api.logout()
    return response


if __name__ == "__main__":
    app.run(port=8081, debug=True)
