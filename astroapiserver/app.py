import functools
import json
import jwt
from datetime import datetime, timedelta
from flask import Flask, abort, make_response, jsonify, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from .globals import PROJECT_PATH, CONFIG, ENV, JWT_SECRET, JWT_ALGORITHM, JWT_EXP

app = Flask(__name__, template_folder=str(PROJECT_PATH / 'templates'))
# app.secret_key = ENV['SECRET']
app.secret_key = "test"
csrf = CSRFProtect(app)  # Adds CSRF token to Flask global vars (csrf_token)


def login_required(f):
    """
    Decorator append to function that requires a logged-in user.
    Login status is checked via confirming the JWT token stored
    on user's cookie.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        is_logged_in, username = check_logged_in()
        if is_logged_in:
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def request_auth(username, password):
    if username != 'test' and password != 'test':
        abort(401)

    payload = {"sub": username}
    payload["exp"] = datetime.utcnow() + timedelta(seconds=JWT_EXP)
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return jwt_token


def check_auth(jwt_token):
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, JWT_ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
        return None


def check_logged_in():
    jwt_token = request.cookies.get("Authentication")
    if jwt_token:
        payload = check_auth(jwt_token)
        if payload:
            return True, payload['sub']

    return False, None

#########
# ROUTES
#########

@app.route("/")
def home():
    context = {}

    is_logged_in, username = check_logged_in()
    if is_logged_in:
        context['username'] = username
    else:
        context['username'] = 'N/A'

    return render_template('home.html', **context)


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        jwt_token = request_auth(request.form.get('username'), request.form.get('password'))
        response = make_response(redirect(url_for('home')))
        response.set_cookie("Authentication", jwt_token)
        return response
    else:
        abort(404)


@app.route("/secret")
@login_required
def secret():
    return '42'