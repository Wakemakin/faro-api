import sys

import flask
import logging

import faro_common.decorators as dec
import faro_common.flask as flaskutils


logger = logging.getLogger('faro_auth')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

ch.setFormatter(formatter)
logger.addHandler(ch)


@dec.static_var("instance", None)
def app(testing=False, create_db=False):
    if testing or app.instance is None:
        app.instance = flaskutils.make_json_app(flask.Flask(__name__))
    return app.instance
