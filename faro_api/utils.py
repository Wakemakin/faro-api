import datetime
import flask
import uuid

import faro_api.database as db
import faro_api.exceptions.common as exc


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
    except ImportError:
        return None
    cls = getattr(mod, cls_name, None)
    return cls


def validate_auth_basics():
    context = get_auth_context()
    if not context:
        return False
    today = datetime.date.today()
    fmt = "%Y-%m-%d"
    valid = datetime.datetime.strptime(context['valid_until'], fmt).date()
    if today >= valid:
        return False
    return True


def require_admin(fn):
    def wrapped(*args, **kwargs):
        if not validate_auth_basics():
            raise exc.AuthenticationRequired()
        context = get_auth_context()
        if not context['is_admin']:
            raise exc.AuthenticationRequired()
        return fn(*args, **kwargs)
    return wrapped


def check_admin_or_owner(resource_owner):
    if not validate_auth_basics():
        raise exc.AuthenticationRequired()
    context = get_auth_context()
    if not context['is_admin'] or resource_owner is None:
        raise exc.AuthenticationRequired()
    user = db.get_owner(resource_owner)
    if not context['userid'] == user.id:
        raise exc.AuthenticationRequired()


def check_owner(resource_owner):
    if not validate_auth_basics():
        raise exc.AuthenticationRequired()
    context = get_auth_context()
    if resource_owner is None:
        raise exc.AuthenticationRequired()
    user = db.get_owner(resource_owner)
    if not context['userid'] == user.id:
        raise exc.AuthenticationRequired()
