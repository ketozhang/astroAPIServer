import os
import sqlite3
from pathlib import Path
from astroapiserver import API
from flask import Flask, abort, jsonify, render_template, request

PROJECT_PATH = Path(__file__).parent.resolve()
DATA_PATH = PROJECT_PATH / "data"


def get_database(database, user=None):
    db_path = DATA_PATH / f"{database}.db"
    if user is None:  # use admin user
        con = sqlite3.connect(db_path)
    else:
        con = sqlite3.connect(db_path)

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    cursor = con.cursor()
    cursor.row_factory = dict_factory
    return cursor


def authenticate(username, password):
    if username == "test" and password == "test":
        user_info = {"username": username}
        return user_info
    else:
        return False


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
api = API(
    app, get_database=get_database, authenticate=authenticate, query_placeholder="?"
)


@app.route("/")
def home():
    context = {"username": api.get_user_info().get("username")}
    return render_template("home.html", **context)


@app.route("/login", methods=["POST"])
def login():
    username, password = (request.form.get("username"), request.form.get("password"))
    response = api.login(username, password)

    if response is False:
        abort(401)
    else:
        return response


@app.route("/logout", methods=["POST"])
def logout():
    response = api.logout()
    return response


@app.route("/planets")
@api.login_required()
def get_planets():
    database = "test"
    query = "SELECT * from planets;"
    return api.execute_query(database, query, use_global_params=True)


@app.route("/planets/<planet>")
def get_planet(planet):
    database = "test"
    query = "SELECT * from planets WHERE name=?;"
    param = [planet]
    return api.execute_query(database, query, param, use_global_params=True)
