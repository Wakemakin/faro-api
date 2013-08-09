import flask
import uuid


def generate_temp_database():
    import os
    _basedir = os.path.abspath(os.path.dirname(__file__))
    filename = str(uuid.uuid4()) + ".db"
    return os.path.join(_basedir, filename)


def get_auth_context():
    env = flask.request.environ
    if 'auth' not in env:
        return None
    return env['auth']
