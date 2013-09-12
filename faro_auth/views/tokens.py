import logging

import flask
import sqlalchemy.exc
import sqlalchemy.orm.exc

from faro_api.exceptions import common as f_exc
from faro_api.models import user as user_model
from faro_api import utils
from faro_api.views import common

logger = logging.getLogger('faro_api.'+__name__)


class UniqueUsernameRequired(f_exc.FaroApiException):
    code = 409
    information = "Username must be unique"


class UserApi(common.BaseApi):
    def __init__(self):
        super(UserApi, self).__init__()
        self.base_resource = user_model.User
        self.alternate_key = "username"

    def _configure_endpoint(self):
        mod = flask.Blueprint('users', __name__)

        user_view = self.as_view('user_api')
        mod.add_url_rule('/users',
                         defaults={'id': None, 'eventid': None},
                         view_func=user_view, methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/users',
                         view_func=user_view, methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/users/<id>', view_func=user_view,
                         defaults={'eventid': None},
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/users/<id>', view_func=user_view,
                         methods=['DELETE', 'PUT', 'OPTIONS'])
        mod.add_url_rule('/events/<string:eventid>/owner',
                         defaults={'id': None},
                         methods=['GET', 'OPTIONS'], view_func=user_view)
        self.blueprint = mod

    @utils.require_admin
    def get(self, id, eventid, **kwargs):
        user_id = id
        event = self.attach_event(eventid, required=False)
        if event is not None:
            user_id = event.owner_id
        return super(UserApi, self).get(user_id, with_events=True)

    @utils.require_admin
    def post(self):
        try:
            return super(UserApi, self).post(with_events=True)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise UniqueUsernameRequired()

    @utils.require_admin
    def delete(self, id):
        return super(UserApi, self).delete(id)

    @utils.require_admin
    def put(self, id):
        return super(UserApi, self).put(id)
