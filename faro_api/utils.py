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


def load_constructor_from_string(name):
    if name is None or not isinstance(name, basestring):
        return None
    cls_name = name.split('.')[-1]
    module_path = '.'.join(name.split('.')[0:-1])
    try:
        mod = __import__(module_path, fromlist=[cls_name])
    except ValueError:
        return None
    cls = getattr(mod, cls_name, None)
    return cls
