import os
import functools
import pandas as pd
from flask import (
    abort,
    Response,
    make_response,
    jsonify,
    redirect,
    request,
    url_for,
)
from astropy.table import Table
from flask_wtf.csrf import CSRFProtect
from webargs.flaskparser import parser
from webargs import fields
from .authentication import get_payload, create_auth


class API:
    def __init__(self, app, get_database, **kwargs):
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
        self.csrf = CSRFProtect(app)
        self.log = app.logger
        self.get_database = get_database
        self.authenticate = kwargs.get("authenticate", lambda *args, **kwargs: True)
        self.authorize = kwargs.get("authorize", lambda *args, **kwargs: [])
        self.placeholder = kwargs.get("query_placeholder", "%s")
        # TODO Allow to modify these configs from environment
        self.config = {
            "JWT_SECRET": os.environ.get("JWT_SECRET", self.app.config["SECRET_KEY"]),
            "JWT_EXP": int(os.environ.get("JWT_EXP", 0)),
            "JWT_ALGORITHM": os.environ.get("JWT_ALGORITHM", "HS256"),
            "LIMIT_DEFAULT": int(os.environ.get("LIMIT_DEFAULT", 100)),
        }

    # Authentication and Authorization

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
            response = make_response(redirect(request.referrer))
            response.set_cookie("Authentication", jwt_token)
            return response
        else:
            return False

    def logout(self):
        """
        Logout via throwing away the JWT token stored in cookie (if exists).
        On success, return redirection to home as response
        """
        if request.referrer is not None:
            response = make_response(redirect(request.referrer))
        else:
            response = make_response(redirect(url_for("home_page")))
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
                # Check CSRF for non-GET request
                # if check_csrf and request.method != "GET":
                #     try:
                #         self.log.info(f"CSRF: {request.form.get('csrf_token')}")
                #         validate_csrf(request.form.get("csrf_token"))
                #     except ValidationError as e:
                #         self.log.info(e)
                #         abort(403)
                # Check if user is logged in
                if not self.is_logged_in():
                    abort(
                        401,
                        "The endpoint requires authentication. You are not logged in.",
                    )

                # Check if user is authorized
                # Valid only if user has at least one of the roles required
                roles = self.authorize(self.get_user_info())
                if roles_required and set(roles).isdisjoint(roles_required):
                    abort(
                        401,
                        "The endpoint requires correct authorization." +
                        "You are logged in but do not have the permission.",
                    )
                else:
                    return f(*args, **kwargs)

            return wrapper

        return decorator

    def get_user_info(self):
        """
        Verify the JWT token.
        If valid return the payload as user info, else empty dict.
        """
        return get_payload(config=self.config)

    def is_logged_in(self):
        return bool(self.get_user_info())

    ################
    # QUERY HANDLING
    ################
    def is_valid_table(self, database, table):
        cursor = self.get_database(database)
        cursor.execute("SHOW TABLES")
        valid_tables = [list(row.values())[0] for row in cursor.fetchall()]

        return table in valid_tables

    def is_valid_columns(self, database, query, params, columns):
        """SQL injection prevention should be done before calling this function"""
        print(query, params)
        cursor = self.get_database(database)
        cursor.execute(query, params)
        valid_columns = [d[0] for d in cursor.description]

        return all([col in valid_columns for col in columns])

    def parse_global_params(self, query, params, database):
        webargs_schema = {
            "select": fields.DelimitedList(fields.Str()),
            "limit": fields.Int(missing=self.config["LIMIT_DEFAULT"]),
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

        # Remove trailing semicolon
        if query[-1] == ";":
            query = query[:-1]

        # Make room for appension
        query += " "
        params = params.copy()

        if global_params.get("orderby") is not None:
            columns = global_params["orderby"]

            if self.is_valid_columns(database, query, params, columns):
                columns = ",".join(f"`{col}`" for col in columns)
                query += f"ORDER BY {columns} "
            else:
                abort(404)

        if global_params.get("desc") is not None:
            if global_params["desc"]:
                query += "DESC "

        if global_params.get("limit") > 0:
            query += f"LIMIT {self.placeholder} "
            params.append(global_params["limit"])

        if global_params.get("select") is not None:
            columns = global_params["select"]
            if self.is_valid_columns(database, query, params, columns):
                columns = ",".join(f"`{col}`" for col in columns)
                query = query.replace("SELECT *", f"SELECT {columns}")
            else:
                abort(404)

        # Trailing space cleanup with semicolon
        if query[-1] == " ":
            query = query[:-1] + ";"

        return query, params

    def execute_query(self, database, query, params=[], use_global_params=False):
        """
        Parameters
        ----------
        database: str
        query: str
        params: list or dict
        use_global_params: bool
            `True` enables global query parameters.

        Returns
        -------
        results: dict
        """
        old_query = query
        old_params = params
        self.log.info(f"Parsing query with input: {old_query} {old_params}")
        if use_global_params:
            query, params = self.parse_global_params(old_query, old_params, database)

        self.log.info(f"Executing query: {query} {params}")
        cursor = self.get_database(database)
        try:
            cursor.execute(query, params)
        except Exception:
            abort(404)
        # except Exception as e:
        #     print(e, query, params, self.placeholder)
        #     old_placeholder = self.placeholder
        #     self.placeholder = next(self.placeholders, None)
        #     if self.placeholder is None:
        #         raise e

        result = {
            "query": f"{query} {params if params else ''}",
            "data": cursor.fetchall(),
        }

        output_format = request.args.get("output_format", "JSON")
        response_data = self.format_data(result, output_format)
        if response_data is None:
            abort(400)
        else:
            return response_data

    @staticmethod
    def format_data(data, data_format):
        if data_format == "JSON":
            return jsonify(data)
        elif data_format in ["ASCII", "TEXT"]:
            colnames = data["data"][0].keys()
            table = Table(data["data"], names=colnames)
            return Response("\n".join(table.pformat_all()), mimetype="text/plain")
        elif data_format == "CSV":
            table = pd.DataFrame(data["data"])
            return Response(table.to_csv(index=False), mimetype="text/plain")
            # return '\n'.join(table.pformat_all(tableid="result-ascii"))
        else:
            return None
