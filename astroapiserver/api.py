import functools
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
from flask_wtf.csrf import CSRFProtect, generate_csrf
from .globals import PROJECT_PATH
from .authentication import get_payload, create_auth


class API:
    def __init__(self, app, auth_func, **kwargs):
        self.app = app
        self.auth_func = auth_func
        self.config = {
            "JWT_SECRET": kwargs.get(
                "jwt_secret", self.app.config["SECRET_KEY"]
            ),
            "JWT_EXP": None,
            "JWT_ALGORITHM": "HS256",
        }

        # Adds CSRF token to Flask global vars (csrf_token)
        self.csrf = CSRFProtect(app)

    def login(self, *args, **kwargs):
        """
        Login with API#authentication.
        On success, set cookie with authentication.
        On fail, return False.
        """
        payload = self.auth_func(*args, **kwargs)
        if isinstance(payload, dict) and payload:
            jwt_token = create_auth(payload, config=self.config)
            # Valid authentication, add JWT token to cookie
            response = make_response(redirect(request.headers.get("Referer")))
            response.set_cookie("Authentication", jwt_token)
            return response
        else:
            return False

    def logout(self):
        """
        Logout via throwing away the JWT token stored in cookie (if exists).
        On success, return redirection to home as response
        """
        response = make_response(redirect(request.headers.get("Referer")))
        response.set_cookie("Authentication", "", expires=0)
        return response

    def login_required(self, f):
        """
        Decorator append to function that requires a logged-in user.
        Login status is checked via confirming the JWT token stored
        on user's cookie.
        """

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            jwt_token = request.cookies.get("Authentication")
            if check_auth(jwt_token, config=self.config):
                return f(*args, **kwargs)
            else:
                abort(401)

        return wrapper

    def get_user_info(self):
        return get_payload(config=self.config)

    def generate_csrf(self, return_response=True, **kwargs):
        csrf_token = generate_csrf(*kwargs)
        if return_response:
            response = make_response()
            response.set_cookie("csrf_token", csrf_token)
            return response
        else:
            return csrf_token
