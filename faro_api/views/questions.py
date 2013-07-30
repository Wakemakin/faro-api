import logging

import flask
import sqlalchemy.exc

from faro_api.exceptions import common as exc
from faro_api.models import question as question_model
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
                         view_func=question_view,
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/users/<string:userid>/questions',
                         defaults={'id': None, 'eventid': None},
                         view_func=question_view,
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/users/<string:userid>/questions',
                         defaults={'eventid': None},
                         view_func=question_view,
                         methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/questions',
                         defaults={'userid': None, 'eventid': None},
                         view_func=question_view,
                         methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/questions/<id>', view_func=question_view,
                         defaults={'userid': None, 'eventid': None},
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/questions/<id>', view_func=question_view,
                         methods=['DELETE', 'PUT', 'OPTIONS'])
        mod.add_url_rule('/events/<string:eventid>/questions',
                         defaults={'userid': None, 'id': None},
                         methods=['GET', 'OPTIONS'],
                         view_func=question_view)
        mod.add_url_rule('/events/<string:eventid>/questions',
                         defaults={'userid': None},
                         methods=['POST', 'OPTIONS'],
                         view_func=question_view)
        self.blueprint = mod

    def put(self, id):
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        owner_required = 'owner_id' in data
        self.attach_owner(None, required=owner_required)
        return super(QuestionApi, self).put(id)

    def get(self, id, userid, eventid):
        self.add_owner_filter(userid)
        self.add_event_filter(eventid)
        return super(QuestionApi, self).get(id)

    @utils.require_body
    def post(self, userid, eventid):
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()

        event = self.attach_event(eventid, required=False)
        if event:
            self.attach_owner(event.owner_id)
        else:
            self.attach_owner(userid)
        try:
            return super(QuestionApi, self).post()
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise QuestionNameRequired()

    def delete(self, id):
        return super(QuestionApi, self).delete(id)
