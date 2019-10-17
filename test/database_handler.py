import pymysql


def get_admin_database(database):
    con = pymysql.connect(
        user="keto", read_default_file="/home/keto/.my.cnf", database=database
    )
    db = con.cursor(pymysql.cursors.DictCursor)
    return db


def get_database(username, password, **kwargs):
    try:
        con = pymysql.connect(user=username, password=password, **kwargs)
        db = con.cursor(pymysql.cursors.DictCursor)
        return db
    except pymysql.err.OperationalError as e:
        return False
