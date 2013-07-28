import logging

import flask
import sqlalchemy.exc
import sqlalchemy.orm.exc as sa_exc

from faro_api import database as db
from faro_api.exceptions import common as exc
from faro_api.models import event as event_model
from faro_api.models import question as question_model
from faro_api.models import user as user_model
from faro_api import utils
from faro_api.views import common

logger = logging.getLogger('faro_api.'+__name__)


class QuestionOwnerRequired(exc.FaroException):
    code = 409
    information = "Question owner required"


class QuestionNameRequired(exc.FaroException):
    code = 409
    information = "Question name required"

logger = logging.getLogger('faro_api.'+__name__)


class QuestionApi(common.BaseApi):
    def __init__(self):
        super(QuestionApi, self).__init__()
        self.base_resource = question_model.Question

    def _configure_endpoint(self):
        mod = flask.Blueprint('questions', __name__)

        question_view = self.as_view('question_api')
        mod.add_url_rule('/questions',
                         defaults={'id': None, 'eventid': None,
                                   'userid': None},
                         view_func=question_view, methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/users/<string:userid>/questions',
                         defaults={'id': None, 'eventid': None},
                         view_func=question_view, methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/users/<string:userid>/questions',
                         defaults={'eventid': None},
                         view_func=question_view, methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/questions',
                         defaults={'userid': None, 'eventid': None},
                         view_func=question_view, methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/questions/<id>', view_func=question_view,
                         defaults={'userid': None, 'eventid': None},
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/questions/<id>', view_func=question_view,
                         methods=['DELETE', 'PUT', 'OPTIONS'])
        mod.add_url_rule('/events/<string:eventid>/questions',
                         defaults={'userid': None, 'id': None},
                         methods=['GET', 'OPTIONS'], view_func=question_view)
        mod.add_url_rule('/events/<string:eventid>/questions',
                         defaults={'userid': None},
                         methods=['POST', 'OPTIONS'], view_func=question_view)
        self.blueprint = mod

    def put(self, id):
        session = flask.g.session
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        attachments = None
        if 'owner_id' in data:
            user_id = data['owner_id']
            try:
                user = db.get_one(session, user_model.User, user_id,
                                  "username")
                data['owner_id'] = user.id
                attachments = {'owner': user}
            except sa_exc.NoResultFound:
                raise exc.NotFound(information="Owner not found")
        return super(QuestionApi, self).put(id, attachments=attachments)

    def get(self, id, userid, eventid):
        session = flask.g.session
        filters = flask.request.args
        if userid is not None:
            user_id = userid
            try:
                user = db.get_one(session, user_model.User, user_id,
                                  "username")
                self.additional_filters['owner_id'] = user.id
            except sa_exc.NoResultFound:
                raise exc.NotFound()
            return super(QuestionApi, self).get(id)
        if eventid is not None:
            event_id = eventid
            try:
                event = db.get_one(session, event_model.Event, event_id)
                self.additional_filters['event_id'] = event.id
            except sa_exc.NoResultFound:
                raise exc.NotFound()
            return super(QuestionApi, self).get(id)
        if 'owner_id' in filters:
            user_id = filters.getlist('owner_id')[0]
            user = db.get_one(session, user_model.User, user_id,
                              "username")
            self.additional_filters['owner_id'] = user.id
        return super(QuestionApi, self).get(id)

    @utils.require_body
    def post(self, userid, eventid):
        session = flask.g.session
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        attachments = {}
        event_id = event_owner = None
        if 'owner_id' not in data and userid is None:
            if 'event_id' not in data and eventid is None:
                raise QuestionOwnerRequired()
        if eventid is not None:
            event_id = eventid
        elif 'event_id' in data:
            event_id = data['event_id']
        if event_id is not None:
            try:
                event = db.get_one(session, event_model.Event, event_id)
                data['event_id'] = event.id
                event_owner = event.owner_id
                attachments['event'] = event
            except sa_exc.NoResultFound:
                raise exc.NotFound(information="Event not found")

        if userid is not None:
            user_id = userid
        elif event_owner is not None:
            user_id = event_owner
        else:
            user_id = data['owner_id']
        try:
            user = db.get_one(session, user_model.User, user_id, "username")
            data['owner_id'] = user.id
            attachments['owner'] = user
        except sa_exc.NoResultFound:
            raise exc.NotFound(information="Owner not found")
        try:
            return super(QuestionApi, self).post(attachments=attachments)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise QuestionNameRequired()

    def delete(self, id):
        return super(QuestionApi, self).delete(id)
