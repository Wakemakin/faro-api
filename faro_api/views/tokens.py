import logging

import flask

from faro_api.models import token as token_model
import faro_api.utils as utils
from faro_api.views import common
from faro_common.exceptions import common as exc
from faro_common import flask as flaskutils

logger = logging.getLogger('faro_api.'+__name__)


class TokenApi(common.BaseApi):
    def __init__(self):
        super(TokenApi, self).__init__()
        self.base_resource = token_model.Token

    def _configure_endpoint(self):
        mod = flask.Blueprint('tokens', __name__)

        token_view = self.as_view('token_api')
        mod.add_url_rule('/tokens',
                         defaults={'id': None, 'userid': None},
                         view_func=token_view, methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/tokens',
                         view_func=token_view, methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/tokens/<id>', view_func=token_view,
                         methods=['DELETE', 'OPTIONS'])
        self.blueprint = mod

    def get(self, id, userid):
        utils.check_owner(userid)
        self.add_owner_filter(userid)
        return super(TokenApi, self).get(id, with_user=True)

    @flaskutils.require_body
    def post(self):
        data = flaskutils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        if 'username' not in data or 'password' not in data:
            raise exc.InvalidInput()
        user = self.attach_owner(data['username'])
        if not user:
            raise exc.NotFoundException()
        self.ignore_data.append('username')
        self.ignore_data.append('password')
        return super(TokenApi, self).post(with_owner=True)

    def delete(self, id):
        return super(TokenApi, self).delete(id)
