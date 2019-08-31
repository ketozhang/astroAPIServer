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
from .authentication import login_required, get_payload, create_auth


class API:
    def __init__(self, app, auth_func):
        self.app = app
        self.auth_func = auth_func

        # Adds CSRF token to Flask global vars (csrf_token)
        self.csrf = CSRFProtect(app)

    def authenticate(self, *args, **kwargs):
        payload = self.auth_func(*args, **kwargs)
        if isinstance(payload, dict) and payload:
            return create_auth(payload)
        else:
            return None

    def login(self, *args, **kwargs):
        """
        Login with API#authentication.
        On success, return redirection to home as response.
        On fail, return False.
        """
        # Either JWT will be valid or the abort happens.
        jwt_token = self.authenticate(*args, **kwargs)

        if jwt_token is None:
            return False
        else:
            # JWT token thus login is valid hereon
            response = make_response(redirect(url_for("home")))
            response.set_cookie("Authentication", jwt_token)
            return response

    def logout(self):
        """
        Logout via throwing away the JWT token stored in cookie (if exists).
        On success, return redirection to home as response
        """
        response = make_response(redirect(url_for("home")))
        response.set_cookie("Authentication", "", expires=0)
        return response
