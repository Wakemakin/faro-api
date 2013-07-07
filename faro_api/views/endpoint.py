import logging

from flask import Blueprint


mod = Blueprint('endpoint', __name__)
logger = logging.getLogger(__name__)


@mod.route('/', methods=['GET'])
def index():
    return 'The greats were great cause they paint a lot'
