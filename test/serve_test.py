import requests
from pathlib import Path
import flask
from flask import (
    Flask,
    abort,
    make_response,
    jsonify,
    redirect,
    render_template,
    url_for,
)
from astroapiserver import get_payload, login_required, ENV
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf, validate_csrf, ValidationError

PROJECT_PATH = Path(__file__).parents[1].resolve()
API_URL = "http://localhost:8081"

app = Flask(__name__, template_folder=str(PROJECT_PATH / "test" / "templates"))
app.secret_key = ENV["SECRET"]
# csrf = CSRFProtect(app)


@app.context_processor
def global_var():
    var = {
        "csrf_token": generate_csrf,
        "API_URL": API_URL
        }
    return var


################
# WEB / ROUTES #
################
@app.route("/")
def home():
    endpoint = API_URL + "/login"

    # # Get CSRF Token
    # print(f"Requesting GET {endpoint}")
    # response = requests.get(endpoint)
    # csrf_token = response.cookies['csrf_token']
    # print(f"Receive {csrf_token}")

    context = {}

    payload = get_payload()
    if payload is not None:
        context["username"] = payload["username"]

    return render_template("home.html", **context)


@app.route("/secret")
@login_required
def secret():
    return "42"


if __name__ == "__main__":
    app.run(port=8080, debug=True)
