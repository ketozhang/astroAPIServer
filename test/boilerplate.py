import os
import sqlite3
from pathlib import Path
from astroapiserver import API
from flask import Flask, abort, render_template, request

PROJECT_PATH = Path(__file__).parent.resolve()
DATA_PATH = PROJECT_PATH / "data"


##################
# DATABASE HANDLER
##################
def get_database(database):
    db_path = DATA_PATH / f"{database}.db"
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
    """
    Returns the user payload (dict) if login is valid else returns False.
    """
    if username == "test" and password == "test":
        user_payload = {"username": username}
        return user_payload
    else:
        return False


#########################
# WEB AND ADMIN INTERFACE
#########################
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
api = API(
    app, get_database=get_database, authenticate=authenticate, query_placeholder="?"
)


@app.route("/")
def home_page():
    context = {"username": api.get_user_payload().get("username")}
    return render_template("home.html", **context)


@app.route("/admin")
def admin_page():
    context = {"openapi": api.openapi}
    return render_template("admin.html", **context)


###############
# API ENDPOINTS
###############
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


@app.route("/<database>/sql")
@api.login_required()
def get_query(database):
    query = request.args.get("query")
    return api.execute_query(database, query)


@app.route("/<database>/<table>")
@api.login_required()
def get_table(database, table):
    database = database
    query = f"SELECT * FROM {table}"

    return api.execute_query(database, query, use_global_params=True)


@app.route("/planets/")
@api.login_required()
def get_planets():
    database = "planets"
    query = "SELECT * FROM planets;"
    return api.execute_query(database, query, use_global_params=True)


@app.route("/planets/<planet>")
def get_planet(planet):
    database = "planets"
    query = "SELECT * FROM planets WHERE UPPER(name)=UPPER(?);"
    param = [planet]
    return api.execute_query(database, query, param)
