import os
import logging
import yaml
from astroapiserver import API
from flask import Flask, abort, jsonify, render_template, request
from pathlib import Path
from database_handler import authenticate, authorize, get_admin_database

PROJECT_PATH = Path(__file__).parents[1].resolve()

# Flask App and API
app = Flask(__name__, template_folder=str(PROJECT_PATH / "test" / "templates"))
app.secret_key = os.environ.get("SECRET_KEY")
api = API(app, authenticate=authenticate, authorize=authorize)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = app.logger

###############
# META ROUTES #
###############
@app.route("/")
def home_page():
    user_info = api.get_user_payload()
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
    user_info = api.get_user_payload()

    with open(PROJECT_PATH / "test/static/swagger.yaml", "r") as f:
        paths = yaml.safe_load(f)["paths"]

    endpoints = set(map(str, app.url_map.iter_rules()))
    endpoints -= {"/", "/login", "/logout"}
    context = {
        "endpoints": endpoints,
        "logged_in": bool(user_info),
        "username": user_info.get("username"),
        "paths": paths,
    }

    print(paths)

    if user_info:
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
    query = request.args.get("query")
    return api.execute_query(database, query)


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
    return api.execute_query(db, query, params)


@app.route("/salary")
@api.login_required()
def get_salary():

    db = get_admin_database(database="employees")
    params = {
        k: request.args.get(k)
        for k in ["emp_no", "from_date"]
        if request.args.get(k) is not None
    }
    placeholders = [f"{param}=%({param})s" for param in params]
    print(placeholders)
    query = f"""
            SELECT *
            FROM salaries
            {'WHERE ' + ' AND '.join(placeholders) if placeholders else ''}
            """
    print(query)
    return api.execute_query(db, query, params)
