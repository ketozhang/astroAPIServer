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
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf, ValidationError
from .globals import PROJECT_PATH
from .authentication import get_payload, create_auth, check_auth


class API:
    def __init__(self, app, **kwargs):
        """[summary]

        Parameters
        ----------
        app : flask.Flask
            Flask application object

        Keyword Arguments
        ----------
        authenticate : function
            An authentication function that returns the user payload (dict)
            if valid else returns False.
        authorize: function
            An authorization function that returns the user's role (list)
            if valid else returns an empty list.
        """
        self.app = app
        self.authenticate = kwargs.get("authenticate", lambda *args, **kwargs: True)
        self.authorize = kwargs.get("authorize", lambda *args, **kwargs: [])
        self.config = {
            "JWT_SECRET": kwargs.get(
                "jwt_secret", self.app.config["SECRET_KEY"]
            ),
            "JWT_EXP": None,
            "JWT_ALGORITHM": "HS256",
        }


    def login(self, *args, **kwargs):
        """
        Login with API::authenticate.
        On success, set cookie with user payload.
        On fail, return False.
        """
        payload = self.authenticate(*args, **kwargs)
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

    def login_required(self, *args, check_csrf=True):
        """
        Decorator append to function that requires a logged-in user.
        Login status is checked via confirming the JWT token stored
        on user's cookie.
        """
        roles_required = list(args)
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                # Check CSRF
                if check_csrf and request.method != "GET":
                    try:
                        self.app.logger.info(f"CSRF: {request.form.get('csrf_token')}")
                        validate_csrf(request.form.get('csrf_token'))
                    except ValidationError as e:
                        self.app.logger.info(e)
                        abort(403)
                # Check if user is logged in
                payload = get_payload(config=self.config)
                if payload is None:
                    abort(401)

                # Check if user is authorized
                # Valid only if user has at least one of the roles required
                roles = self.authorize(payload)
                if roles_required and set(roles).isdisjoint(roles_required):
                    abort(401)
                else:
                    return f(*args, **kwargs)

            return wrapper

        return decorator

    def get_user_info(self):
        """Verify the JWT token. If valid return the payload, else None"""
        return get_payload(config=self.config)
