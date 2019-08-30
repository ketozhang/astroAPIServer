import functools
import jwt
from datetime import datetime, timedelta
from flask import abort, request
from .globals import PROJECT_PATH, CONFIG, ENV, JWT_SECRET, JWT_ALGORITHM, JWT_EXP


def login_required(f):
    """
    Decorator append to function that requires a logged-in user.
    Login status is checked via confirming the JWT token stored
    on user's cookie.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        username = get_current_user()
        if username is None:
            abort(401)
        else:
            return f(*args, **kwargs)

    return wrapper


def authenticate(username, password):
    """
    Returns a JWT token if credentials are valid, otherwise ABORT 401.
    """
    print(f"Authentication with {username}, {password}")
    if username != 'test' or password != 'test':
        abort(401)
    print("Success")

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


def get_current_user():
    jwt_token = request.cookies.get("Authentication")
    if jwt_token:
        payload = check_auth(jwt_token)
        if payload:
            return payload['sub']

    return None