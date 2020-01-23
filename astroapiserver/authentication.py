import functools
import jwt
from datetime import datetime, timedelta
from flask import request, abort
from .globals import PROJECT_PATH


def create_auth(payload, **kwargs):
    if "config" in kwargs:
        config = kwargs["config"]
        jwt_secret = config["JWT_SECRET"]
        jwt_exp = config["JWT_EXP"]
        jwt_algorithm = config["JWT_ALGORITHM"]
    else:
        raise NotImplementedError()

    if jwt_exp != 0:
        payload.update(
            {
                "exp": datetime.utcnow() + timedelta(seconds=jwt_exp),
                "iat": datetime.utcnow(),
            }
        )

    jwt_token = jwt.encode(payload, jwt_secret, jwt_algorithm)
    return jwt_token


def check_auth(jwt_token, return_payload=False, **kwargs):
    """Verify the JWT token. If valid return True, else False"""
    if "config" in kwargs:
        config = kwargs["config"]
        jwt_secret = config["JWT_SECRET"]
        jwt_exp = config["JWT_EXP"]
        jwt_algorithm = config["JWT_ALGORITHM"]
    else:
        raise NotImplementedError()

    try:
        payload = jwt.decode(jwt_token, jwt_secret, jwt_algorithm)
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


def get_payload(**kwargs):
    """Verify the JWT token. If valid return the payload, else None"""
    jwt_token = request.cookies.get("Authentication")
    payload = check_auth(jwt_token, return_payload=True, **kwargs)
    if payload is False:
        return {}
    else:
        return payload
