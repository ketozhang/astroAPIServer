from database_handler import get_database, get_admin_database


def authenticate(username, password):
    """
    Use by API by storing payload to user's cookie. Returns cookie (a dict).
    """
    db = get_database(username, password)

    if db:
        db.close()
        payload = {"username": username}
        return payload
    else:
        return False


def authorize(payload):
    """Given a payload, return the roles of the user"""
    db = get_admin_database()
    username = payload["username"]

    query = "SELECT * FROM users WHERE username=%s"
    db.execute(query, [username])
    row = db.fetchone()

    roles = []
    for role in ["admin", "dev"]:
        if row[f"is_{role}"] == 1:
            roles.append(role)
    return roles