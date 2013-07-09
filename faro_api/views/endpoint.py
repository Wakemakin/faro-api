import logging

from flask import Blueprint, Response


mod = Blueprint('endpoint', __name__)
logger = logging.getLogger('faro_api.'+__name__)


@mod.route('/', methods=['GET'])
def index():
    return 'The greats were great cause they paint a lot'


@mod.route('/favicon.ico', methods=['GET'])
def favicon():
    return Response(status=204)
