import sys
from pathlib import Path
import logging
from astropy.table import Table
import yaml
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from astroapiserver import API, create_auth, ENV
from auth import authenticate, authorize
from database_handler import get_database, get_admin_database

PROJECT_PATH = Path(__file__).parents[1].resolve()

# Flask App and API
app = Flask(__name__, template_folder=str(PROJECT_PATH / "test" / "templates"))
app.secret_key = ENV["SECRET"]
api = API(app, authenticate=authenticate, authorize=authorize)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = app.logger


def execute_query(cursor, query, params):
    cursor.execute(query, params)
    result = {"query": cursor.mogrify(query, params), "data": cursor.fetchall()}

    output_format = request.args.get('output_format', 'JSON')
    if output_format == "JSON":
        return jsonify(result)
    elif output_format == "ASCII":
        table = Table(result['data'])
        return str(table)
    elif output_format == "CSV":
        return 'bad'
    else:
        abort(400)  # Return 400 BAD REQUEST

###############
# META ROUTES #
###############
@app.route("/")
def home_page():
    user_info = api.get_user_info()
    if user_info is not None:
        return jsonify(user_info)
    else:
        return jsonify(None)


@app.route("/admin")
def admin_page():
    """
    Admin page with OpenAPI tools.
    User may use this to login thus this page is not constrained to only admin.
    """
    user_info = api.get_user_info()

    with open(PROJECT_PATH / "test/static/swagger.yaml", "r") as f:
        paths = yaml.safe_load(f)['paths']

    endpoints = set(map(str, app.url_map.iter_rules()))
    endpoints -= {"/", "/login", "/logout"}
    context = {
        "endpoints": endpoints,
        "logged_in": user_info is not None,
        "username": user_info,
        "paths": paths
    }

    print(paths)

    if user_info is None:
        return render_template("login.html")
    else:
        return render_template("admin.html", **context)


@app.route("/login", methods=["POST"])
def login():
    username, password = (request.form.get("username"), request.form.get("password"))
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


###############
# DATA ROUTES #
###############
@app.route("/<database>/sql")
@api.login_required("admin")
def get_query(database):
    db = get_admin_database(database=database)

    query = request.args.get("query")
    db.execute(query)

    result = {"query": db.mogrify(query), "data": db.fetchall()}
    return jsonify(result)


@app.route("/employees/<int:emp_no>")
@api.login_required()
def get_employee(emp_no):
    """
    Properties
    ----------
    emp_no : int
    first_name : str
    last_name: str
    birth_date: date
    gender: enum('M', 'F')
    hire_date: date

    GET Response
    ------------
    Same as properties
    """
    db = get_admin_database(database="employees")
    query = "SELECT * FROM employees where emp_no=%s"
    params = [emp_no]
    return execute_query(db, query, params)



@app.route("/salary")
@api.login_required()
def get_salary():

    db = get_admin_database(database="employees")
    params = {k: request.args.get(k) for k in ['emp_no', 'from_date'] if request.args.get(k) is not None}
    placeholders = [f"{param}=%({param})s" for param in params]
    print(placeholders)
    query = f"SELECT * FROM salaries {'WHERE ' + ' AND '.join(placeholders) if placeholders else ''} "
    print(query)
    return execute_query(db, query, params)
