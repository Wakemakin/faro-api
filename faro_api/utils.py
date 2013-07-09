import json
import re
import uuid

import flask
import werkzeug.exceptions as http

from faro_api.exceptions import common as exc


def generate_temp_database():
    import os
    _basedir = os.path.abspath(os.path.dirname(__file__))
    filename = str(uuid.uuid4()) + ".db"
    return os.path.join(_basedir, filename)


def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


def require_body(func):
    def check_body_exists(*args, **kwargs):
        if len(flask.request.data) == 0:
            raise exc.RequiresBody()
        return func(*args, **kwargs)
    return check_body_exists


def json_request_data(request_data):
    try:
        if request_data == '{}':
            return None
        return json.loads(request_data)
    except ValueError:
        raise exc.InvalidInput(information="Malformed body")


def make_uuid():
    return uuid.uuid1()


def is_uuid(uuid_str):
    if isinstance(uuid_str, uuid.UUID):
        uuid_str = str(uuid_str)
    if uuid_str is None or not isinstance(uuid_str, basestring):
        return False
    re_string = r"%s-%s-%s-%s-%s" % ("^[0-9a-f]{8}",
                                     "[0-9a-f]{4}",
                                     "[1-5][0-9a-f]{3}",
                                     "[89ab][0-9a-f]{3}",
                                     "[0-9a-f]{12}$")
    m = re.match(re_string, uuid_str)
    if not m:
        return False
    return m.group(0) == uuid_str


def make_json_app(app, **kwargs):
    def make_json_error(ex):
        if hasattr(ex, "information"):
            response = flask.jsonify(message=str(ex),
                                     information=ex.information)
        else:
            response = flask.jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, http.HTTPException)
                                else 500)
        return response

    for code in http.default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app
