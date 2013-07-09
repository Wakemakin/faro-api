import logging

from flask import Blueprint, request, g
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from faro_api.views.common import BaseApi
from faro_api import database as db
from faro_api.models.event import Event
from faro_api.models.user import User
from faro_api import utils
from faro_api.exceptions import common as exc

logger = logging.getLogger('faro_api.'+__name__)


class EventOwnerRequired(exc.FaroException):
    code = 409
    information = "Event owner required"


class EventNameRequired(exc.FaroException):
    code = 409
    information = "Event name required"


class EventApi(BaseApi):
    def __init__(self):
        super(EventApi, self).__init__()
        self.base_resource = Event

    def _configure_endpoint(self):
        mod = Blueprint('events', __name__)

        event_view = self.as_view('event_api')
        mod.add_url_rule('/api/users/<string:userid>/events',
                         defaults={'id': None},
                         view_func=event_view, methods=['GET'])
        mod.add_url_rule('/api/users/<string:userid>/events',
                         view_func=event_view, methods=['POST'])
        mod.add_url_rule('/api/events', defaults={'id': None,
                         'userid': None},
                         view_func=event_view, methods=['GET'])
        mod.add_url_rule('/api/events', defaults={'userid': None},
                         view_func=event_view, methods=['POST'])
        mod.add_url_rule('/api/events/<id>', view_func=event_view,
                         methods=['GET', 'DELETE', 'PUT'],
                         defaults={'userid': None})
        self.blueprint = mod

    def get(self, id, userid):
        session = g.session
        filters = request.args
        if userid is None:
            if 'owner_id' in filters:
                user_id = filters.getlist('owner_id')[0]
                user = db.get_one(session, User, user_id, "username")
                self.additional_filters['owner_id'] = user.id
            return super(EventApi, self).get(id, with_owner=True)
        else:
            user_id = userid
            try:
                user = db.get_one(session, User, user_id, "username")
                self.additional_filters['owner_id'] = user.id
            except NoResultFound:
                raise exc.NotFound()
            return super(EventApi, self).get(id, with_owner=True)
        raise exc.NotFound()

    def put(self, id, userid):
        session = g.session
        data = utils.json_request_data(request.data)
        if not data:
            raise exc.BodyRequired()
        with_owner = False
        attachments = None
        if 'owner_id' in data:
            user_id = data['owner_id']
            try:
                user = db.get_one(session, User, user_id, "username")
                data['owner_id'] = user.id
                attachments = {'owner': user}
                with_owner = True
            except NoResultFound:
                raise exc.NotFound(information="Owner not found")
        return super(EventApi, self).put(id, with_owner=with_owner,
                                         attachments=attachments)

    def delete(self, id, userid):
        return super(EventApi, self).delete(id)

    @utils.require_body
    def post(self, userid):
        session = g.session
        data = utils.json_request_data(request.data)
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
            user = db.get_one(session, User, user_id, "username")
            data['owner_id'] = user.id
            attachments = {'owner': user}
            with_owner = True
        except NoResultFound:
            raise exc.NotFound(information="Owner not found")
        try:
            return super(EventApi, self).post(with_owner=with_owner,
                                              attachments=attachments)
        except IntegrityError as e:
            logger.error(e)
            raise EventNameRequired()
