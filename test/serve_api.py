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
from database_handler import get_database, get_admin_database


def authenticate(username, password):
    """
    Use by API by storing payload to user's cookie. Returns cookie (a dict).
    """
    db = get_database(username, password)

    if db:
        db.close()
        payload = {"username": username}
        return payload
    else:
        return False


def authorize(payload):
    """Given a payload, return the roles of the user"""
    db = get_admin_database()
    username = payload["username"]

    query = "SELECT * FROM users WHERE username=%s"
    db.execute(query, [username])
    row = db.fetchone()

    roles = []
    for role in ["admin", "dev"]:
        if row[f"is_{role}"] == 1:
            roles.append(role)
    return roles


app = Flask(__name__, template_folder=str(PROJECT_PATH / "test" / "templates"))
app.secret_key = ENV["SECRET"]
logging.basicConfig(level=logging.DEBUG)
logger = app.logger
api = API(app, authenticate=authenticate, authorize=authorize)

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


@app.route("/query", methods=["POST", "GET"])
@api.login_required("admin")
def make_query():
    db = get_admin_database(database="employees")

    query = request.form.get("query")
    db.execute(query)

    result = {"query": db.mogrify(query), "data": db.fetchall()}
    return jsonify(result)


@app.route("/employees/<int:emp_no>", methods=["POST", "GET"])
@api.login_required()
def get_employee(emp_no):
    db = get_admin_database(database="employees")

    query = "SELECT * FROM employees where emp_no=%s"
    db.execute(query, [emp_no])

    result = {"query": db.mogrify(query, [emp_no]), "data": db.fetchall()}
    return jsonify(result)


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
