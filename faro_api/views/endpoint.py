import logging

import flask


mod = flask.Blueprint('endpoint', __name__)
logger = logging.getLogger('faro_api.'+__name__)


@mod.route('/', methods=['GET'])
def index():
    return 'The greats were great cause they paint a lot'


@mod.route('/favicon.ico', methods=['GET'])
def favicon():
    return flask.Response(status=204)
