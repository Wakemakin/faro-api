import logging

import flask
import sqlalchemy.exc
import sqlalchemy.orm.exc as sa_exc

from faro_api import database as db
from faro_api.exceptions import common as exc
from faro_api.models import event as event_model
from faro_api.models import user as user_model
from faro_api import utils
from faro_api.views import common

logger = logging.getLogger('faro_api.'+__name__)


class EventOwnerRequired(exc.FaroException):
    code = 409
    information = "Event owner required"


class EventNameRequired(exc.FaroException):
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
        session = flask.g.session
        filters = flask.request.args
        if userid is None:
            if 'owner_id' in filters:
                user_id = filters.getlist('owner_id')[0]
                user = db.get_one(session, user_model.User, user_id,
                                  "username")
                self.additional_filters['owner_id'] = user.id
            return super(EventApi, self).get(id, with_owner=True)
        else:
            user_id = userid
            try:
                user = db.get_one(session, user_model.User, user_id,
                                  "username")
                self.additional_filters['owner_id'] = user.id
            except sa_exc.NoResultFound:
                raise exc.NotFound()
            return super(EventApi, self).get(id, with_owner=True)

    def put(self, id, userid):
        session = flask.g.session
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.BodyRequired()
        with_owner = False
        attachments = None
        if 'owner_id' in data:
            user_id = data['owner_id']
            try:
                user = db.get_one(session, user_model.User, user_id,
                                  "username")
                data['owner_id'] = user.id
                attachments = {'owner': user}
                with_owner = True
            except sa_exc.NoResultFound:
                raise exc.NotFound(information="Owner not found")
        return super(EventApi, self).put(id, with_owner=with_owner,
                                         attachments=attachments)

    def delete(self, id, userid):
        return super(EventApi, self).delete(id)

    @utils.require_body
    def post(self, userid):
        session = flask.g.session
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        with_owner = False
        attachments = None
        if 'owner_id' not in data and userid is None:
            raise EventOwnerRequired()
        if userid is not None:
            user_id = userid
        else:
            user_id = data['owner_id']
        try:
            user = db.get_one(session, user_model.User, user_id, "username")
            data['owner_id'] = user.id
            attachments = {'owner': user}
            with_owner = True
        except sa_exc.NoResultFound:
            raise exc.NotFound(information="Owner not found")
        try:
            return super(EventApi, self).post(with_owner=with_owner,
                                              attachments=attachments)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise EventNameRequired()
