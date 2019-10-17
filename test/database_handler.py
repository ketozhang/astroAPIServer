import pymysql
from flask import make_response


def get_admin_database(database):
    """Get database logged in by an admin"""
    try:
        con = pymysql.connect(
            user="keto", read_default_file="/home/keto/.my.cnf", database=database
        )
        db = con.cursor(pymysql.cursors.DictCursor)
        return db
    except pymysql.err.OperationalError, pymysql.err.InternalError as e:
        print(e)


# def get_database(username, password, **kwargs):
#     try:
#         con = pymysql.connect(user=username, password=password, **kwargs)
#         db = con.cursor(pymysql.cursors.DictCursor)
#         return db
#     except pymysql.err.OperationalError as e:
#         return False

def execute_query(database, query, params={}):
    """
    Arguments
    ---------
    cursor: pymysql.cursor
    query: str
    params: list or dict
    """
    cursor = get_admin_database(database)
    cursor.execute(query, params)
    result = {"query": cursor.mogrify(
        query, params), "data": cursor.fetchall()}

    output_format = request.args.get('output_format', 'JSON')
    if output_format == "JSON":
        return jsonify(result)
    elif output_format == "ASCII":
        table = Table(result['data'])
        return '\n'.join(table.pformat_all(tableid="result-ascii"))
    elif output_format == "CSV":
        table = pd.DataFrame(result['data'])
        return table.to_csv(index=False)
        # return '\n'.join(table.pformat_all(tableid="result-ascii"))
    else:
        abort(400)  # Return 400 BAD REQUEST


def is_valid_table(database, table):
    cursor = get_admin_database('database')
    cursor.execute("SHOW TABLES")
    valid_tables = [list(row.values())[0] for row in cursor.fetchall()]
    print(valid_tables)

    return table in valid_tables
