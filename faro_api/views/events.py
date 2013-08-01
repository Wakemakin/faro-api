import logging

import flask
import sqlalchemy.exc

from faro_api.exceptions import common as f_exc
from faro_api.models import event as event_model
from faro_api.views import common
from faro_common.exceptions import common as exc
from faro_common import flask as flaskutils

logger = logging.getLogger('faro_api.'+__name__)


class EventOwnerRequired(f_exc.FaroApiException):
    code = 409
    information = "Event owner required"


class EventNameRequired(f_exc.FaroApiException):
    code = 409
    information = "Event name required"


class EventApi(common.BaseApi):
    def __init__(self):
        super(EventApi, self).__init__()
        self.base_resource = event_model.Event

    def _configure_endpoint(self):
        mod = flask.Blueprint('events', __name__)

        event_view = self.as_view('event_api')
        mod.add_url_rule('/users/<string:userid>/events',
                         defaults={'id': None},
                         view_func=event_view, methods=['GET'])
        mod.add_url_rule('/users/<string:userid>/events',
                         view_func=event_view, methods=['POST'])
        mod.add_url_rule('/events', defaults={'id': None,
                         'userid': None},
                         view_func=event_view, methods=['GET'])
        mod.add_url_rule('/events', defaults={'userid': None},
                         view_func=event_view, methods=['POST'])
        mod.add_url_rule('/events/<id>', view_func=event_view,
                         methods=['GET', 'DELETE', 'PUT'],
                         defaults={'userid': None})
        self.blueprint = mod

    def get(self, id, userid):
        self.add_owner_filter(userid)
        return super(EventApi, self).get(id, with_owner=True)

    def put(self, id, userid):
        data = flaskutils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        owner_required = 'owner_id' in data
        self.attach_owner(userid, required=owner_required)
        return super(EventApi, self).put(id, with_owner=True)

    def delete(self, id, userid):
        return super(EventApi, self).delete(id)

    @flaskutils.require_body
    def post(self, userid):
        data = flaskutils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        self.attach_owner(userid)
        try:
            return super(EventApi, self).post(with_owner=True)
        except sqlalchemy.exc.IntegrityError:
            raise EventNameRequired()
