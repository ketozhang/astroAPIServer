import functools
import jwt
from datetime import datetime, timedelta
from flask import request, abort
from .globals import (
    PROJECT_PATH,
    CONFIG,
    ENV,
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_EXP,
)


def login_required(f):
    """
    Decorator append to function that requires a logged-in user.
    Login status is checked via confirming the JWT token stored
    on user's cookie.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        jwt_token = request.cookies.get("Authentication")
        if check_auth(jwt_token):
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def create_auth(payload):
    if JWT_EXP is not None:
        payload["exp"] = datetime.utcnow() + timedelta(seconds=JWT_EXP)

    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return jwt_token


def check_auth(jwt_token, return_payload=False):
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, JWT_ALGORITHM)
        if return_payload:
            return payload
        else:
            return True
    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        jwt.exceptions.DecodeError,
    ):
        return False


def get_payload():
    jwt_token = request.cookies.get("Authentication")
    payload = check_auth(jwt_token, return_payload=True)
    if payload is False:
        return None
    else:
        return payload
