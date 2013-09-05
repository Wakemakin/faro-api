import logging

import flask
import sqlalchemy.exc
import sqlalchemy.orm.exc

from faro_api.models import role as role_model
from faro_api.views import common

logger = logging.getLogger('faro_api.'+__name__)


class RoleApi(common.BaseApi):
    def __init__(self):
        super(RoleApi, self).__init__()
        self.base_resource = role_model.Model

    def _configure_endpoint(self):
        mod = flask.Blueprint('roles', __name__)
        role_view = self.as_view('role_api')
        #GET
        mod.add_url_rule('/users/<string:userId>/roles',
                         view_func=role_view,
                         defaults={'userId': None, 'roleId': None},
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/roles',
                         view_func=role_view,
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/roles/<userId>',
                         view_func=role_view,
                         methods=['GET', 'OPTIONS'])
        #POST
        mod.add_url_rule('/roles',
                         view_func=role_view,
                         methods=['POST', 'OPTIONS'])
        #PUT
        mod.add_url_rule('/roles/<userId>',
                         view_func=role_view,
                         defaults={'userId': None},
                         methods=['PUT', 'OPTIONS'])
        mod.add_url_rule('/users/<string:userId>/roles',
                         view_func=role_view,
                         defaults={'userId': None},
                         methods=['DELETE', 'OPTIONS'])

    def get(self, id, eventid, **kwargs):
        user_id = id
        event = self.attach_event(eventid, required=False)
        if event is not None:
            user_id = event.owner_id
        return super(RoleApi, self).get(user_id, with_events=True)

    def post(self):
        try:
            return super(RoleApi, self).post(with_events=True)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
