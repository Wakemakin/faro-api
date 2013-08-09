import logging
import os

import flask

import faro_api
import faro_common.exceptions.common as exc


mod = flask.Blueprint('endpoint', __name__)
logger = logging.getLogger('faro_api.'+__name__)


@mod.route('/', methods=['GET'])
def index():
    return 'The greats were great cause they paint a lot'


@mod.route('/release', methods=['GET'])
def release():
    try:
        module_path = os.path.dirname(faro_api.__file__)
        root = os.path.abspath(os.path.join(module_path, os.pardir))
        release_file = "%s/RELEASE" % root
        with open(release_file) as f:
            out = f.read()
        return '%s' % out
    except IOError:
        raise exc.NotFound()


@mod.route('/favicon.ico', methods=['GET'])
def favicon():
    return flask.Response(status=204)
