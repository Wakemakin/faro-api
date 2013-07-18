import logging

import flask
import sqlalchemy.exc
import sqlalchemy.orm.exc

from faro_api import database as db
from faro_api.exceptions import common as exc
from faro_api.models import event as event_model
from faro_api.models import user as user_model
from faro_api.views import common

logger = logging.getLogger('faro_api.'+__name__)


class UniqueUsernameRequired(exc.FaroException):
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
        mod.add_url_rule('/api/users',
                         defaults={'id': None, 'eventid': None},
                         view_func=user_view, methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/api/users',
                         view_func=user_view, methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/api/users/<id>', view_func=user_view,
                         defaults={'eventid': None},
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/api/users/<id>', view_func=user_view,
                         methods=['DELETE', 'PUT', 'OPTIONS'])
        mod.add_url_rule('/api/events/<string:eventid>/owner',
                         defaults={'id': None},
                         methods=['GET', 'OPTIONS'], view_func=user_view)
        self.blueprint = mod

    def get(self, id, eventid, **kwargs):
        session = flask.g.session
        if eventid is not None:
            try:
                event = db.get_one(session, event_model.Event, eventid)
                return super(UserApi, self).get(event.owner_id,
                                                with_events=True)
            except sqlalchemy.orm.exc.NoResultFound:
                raise exc.NotFound()
        return super(UserApi, self).get(id, with_events=True)

    def post(self):
        try:
            return super(UserApi, self).post(with_events=True)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise UniqueUsernameRequired()
