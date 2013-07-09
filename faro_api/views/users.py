import logging

from flask import Blueprint
from sqlalchemy.exc import IntegrityError

from faro_api.views.common import BaseApi
from faro_api.models.user import User
from faro_api.exceptions import common as exc

logger = logging.getLogger('faro_api.'+__name__)


class UniqueUsernameRequired(exc.FaroException):
    code = 409
    information = "Username must be unique"


class UserApi(BaseApi):
    def __init__(self):
        super(UserApi, self).__init__()
        self.base_resource = User
        self.alternate_key = "username"

    def _configure_endpoint(self):
        mod = Blueprint('users', __name__, url_prefix='/api/users')

        user_view = self.as_view('user_api')
        mod.add_url_rule('', defaults={'id': None},
                         view_func=user_view, methods=['GET'])
        mod.add_url_rule('', view_func=user_view, methods=['POST'])
        mod.add_url_rule('/<id>', view_func=user_view,
                         methods=['GET', 'DELETE', 'PUT'])
        self.blueprint = mod

    def get(self, id, **kwargs):
        return super(UserApi, self).get(id, with_events=True)

    def put(self, id):
        return super(UserApi, self).put(id, with_events=True)

    def post(self):
        try:
            return super(UserApi, self).post(with_events=True)
        except IntegrityError as e:
            logger.error(e)
            raise UniqueUsernameRequired()
