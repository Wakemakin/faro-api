from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound

from faro_api.views.common import BaseApi
from faro_api.database import get_one
from faro_api.models import Event, User
from faro_api import utils
from faro_api.exceptions import common as exc


class EventApi(BaseApi):
    def __init__(self):
        super(EventApi, self).__init__()
        self.base_resource = Event

    def get(self, id):
        return super(EventApi, self).get(id, with_owner=True)

    def put(self, id):
        data = utils.json_request_data(request.data)
        with_owner = False
        if 'owner_id' in data:
            user_id = data['owner_id']
            try:
                user = get_one(User, user_id, "username")
                data['owner_id'] = user.id
                attachments = [{'owner': user}]
                with_owner = True
            except NoResultFound:
                raise exc.NotFound(information="Owner not found")
        return super(EventApi, self).put(id, with_owner=with_owner,
                                         attachments=attachments)

    def post(self):
        data = utils.json_request_data(request.data)
        with_owner = False
        attachments = None
        if 'owner_id' in data:
            user_id = data['owner_id']
            try:
                user = get_one(User, user_id, "username")
                data['owner_id'] = user.id
                attachments = {'owner': user}
                with_owner = True
            except NoResultFound:
                raise exc.NotFound(information="Owner not found")
        return super(EventApi, self).post(with_owner=with_owner,
                                          attachments=attachments)


mod = Blueprint('events', __name__, url_prefix='/api/events')

event_view = EventApi().as_view('event_api')
mod.add_url_rule('', defaults={'id': None},
                 view_func=event_view, methods=['GET'])
mod.add_url_rule('', view_func=event_view, methods=['POST'])
mod.add_url_rule('/<id>', view_func=event_view,
                 methods=['GET', 'DELETE', 'PUT'])
