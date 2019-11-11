"""Handles creating connections to the database"""
import pymysql


def get_admin_database(database):
    """Get database logged in by an admin"""
    con = pymysql.connect(
        user="keto", read_default_file="/home/keto/.my.cnf", database=database
    )
    db = con.cursor(pymysql.cursors.DictCursor)
    return db


def get_database(username, password, **kwargs):
    con = pymysql.connect(user=username, password=password, **kwargs)
    db = con.cursor(pymysql.cursors.DictCursor)
    return db


def authenticate(username, password):
    """
    Use by API by storing payload to user's cookie. Returns cookie (a dict).
    """
    try:
        db = get_database(username, password)
        payload = {"username": username}
    except (pymysql.err.OperationalError, pymysql.err.InternalError):
        return False
    finally:
        db.close()

    return payload


def authorize(payload):
    """Given a payload, return the roles of the user"""
    db = get_admin_database(database="test")
    username = payload["username"]

    query = "SELECT * FROM users WHERE username=%s"

    try:
        db.execute(query, [username])
        row = db.fetchone()

        roles = []
        for role in ["admin", "dev"]:
            if row[f"is_{role}"] == 1:
                roles.append(role)
    finally:
        db.close()

    return roles
