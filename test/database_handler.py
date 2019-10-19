import pymysql
from astropy.table import Table
from astropy.io import ascii
from flask import make_response, request, jsonify, abort
from webargs.flaskparser import parser
from webargs import fields
import pandas as pd


def get_admin_database(database):
    """Get database logged in by an admin"""
    try:
        con = pymysql.connect(
            user="keto", read_default_file="/home/keto/.my.cnf", database=database
        )
        db = con.cursor(pymysql.cursors.DictCursor)
        return db
    except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
        print(e)

def get_database(username, password, **kwargs):
    try:
        con = pymysql.connect(user=username, password=password, **kwargs)
        db = con.cursor(pymysql.cursors.DictCursor)
        return db
    except pymysql.err.OperationalError as e:
        return False


# def parse_columns(columns):
#     try:
#         if not isinstance(eval(columns), list):
#             abort(500)
#     except NameError:
#         if isinstance(columns, str):
#             return [columns]
#         else:
#             abort(500)


def parse_global_params(query, database, table):
    webargs_schema = {
        "select": fields.DelimitedList(fields.Str()),
        "limit": fields.Int(missing=100),
        "orderby": fields.DelimitedList(fields.Str()),
        "desc": fields.Bool(),
    }

    global_params = parser.parse(webargs_schema, request)
    # global_params = {
    #     "select": request.args.get("select"),
    #     "limit": int(request.args.get("limit", 100)),
    #     "orderby": request.args.get("orderby"),
    #     "desc": request.args.get("desc"),
    # }

    params = []
    query += " "

    if global_params.get("select") is not None:
        columns = global_params["select"]

        if is_valid_columns(database, table, columns):
            columns = ",".join(f"`{col}`" for col in columns)
            query = query.replace("SELECT *", f"SELECT {columns}")
        else:
            abort(404)

    if global_params.get("orderby") is not None:
        columns = global_params["orderby"]

        if is_valid_columns(database, table, columns):
            columns = ",".join(f"`{col}`" for col in columns)
            query += f"ORDER BY {columns} "
        else:
            abort(404)

    if global_params.get("desc") is not None:
        if global_params["desc"]:
            query += "DESC "

    if global_params.get("limit") is not None:
        query += "LIMIT %s "
        params.append(global_params["limit"])

    # Trailing space cleanup with semicolon
    if query[-1] == " ":
        query = query[:-1] + ";"

    return query, params


def execute_query(database, query, params={}):
    """
    Arguments
    ---------
    cursor: pymysql.cursor
    query: str
    params: list or dict
    """
    cursor = get_admin_database(database)
    print(query, params)
    cursor.execute(query, params)
    result = {"query": cursor.mogrify(query, params), "data": cursor.fetchall()}

    output_format = request.args.get("output_format", "JSON")
    if output_format == "JSON":
        return jsonify(result)
    elif output_format == "ASCII":
        colnames = result["data"][0].keys()
        table = Table(result["data"], names=colnames)
        return "\n".join(table.pformat_all(tableid="result-ascii"))
    elif output_format == "CSV":
        table = pd.DataFrame(result["data"])
        return table.to_csv(index=False)
        # return '\n'.join(table.pformat_all(tableid="result-ascii"))
    else:
        abort(400)  # Return 400 BAD REQUEST


def is_valid_table(database, table):
    cursor = get_admin_database(database)
    cursor.execute("SHOW TABLES")
    valid_tables = [list(row.values())[0] for row in cursor.fetchall()]

    return table in valid_tables


def is_valid_columns(database, table, columns):
    """SQL injection prevention should be done before calling this function"""
    cursor = get_admin_database(database)
    cursor.execute(f"SELECT * FROM {table} LIMIT 1;")
    valid_columns = [i[0] for i in cursor.description]

    return all([col in valid_columns for col in columns])
