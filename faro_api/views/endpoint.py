from flask import Blueprint


mod = Blueprint('endpoint', __name__)


@mod.route('/', methods=['GET'])
def index():
    return 'The greats were great cause they paint a lot'
