import json
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
from flask_wtf.csrf import CSRFProtect
from .globals import PROJECT_PATH, CONFIG, ENV
from .authentication import login_required, get_current_user, authenticate

app = Flask(__name__, template_folder=str(PROJECT_PATH / "templates"))
# app.secret_key = ENV['SECRET']
app.secret_key = "test"
csrf = CSRFProtect(app)  # Adds CSRF token to Flask global vars (csrf_token)


################
# WEB / ROUTES #
################
@app.route("/")
def home():
    context = {}

    username = get_current_user()
    if username is not None:
        context["username"] = username

    return render_template("home.html", **context)


@app.route("/login", methods=["POST"])
def login():
    # Either JWT will be valid or the abort happens.
    jwt_token = authenticate(
        request.form.get("username"), request.form.get("password")
    )

    # JWT token thus login is valid hereon
    response = make_response(redirect(url_for("home")))
    response.set_cookie("Authentication", jwt_token)
    return response


@app.route("/logout", methods=["POST"])
def logout():
    """Logout via throwing away the JWT token stored in cookie (if exists)"""
    response = make_response(redirect(url_for("home")))
    response.set_cookie("Authentication", '', expires=0)
    return response


@app.route("/secret")
@login_required
def secret():
    return "42"
