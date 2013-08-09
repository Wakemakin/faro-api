import logging

import flask
import sqlalchemy.exc

from faro_api.exceptions import common as exc
from faro_api.models import dataprovider as dps_model
from faro_api.views import common
from faro_common import flask as flaskutils

logger = logging.getLogger('faro_api.'+__name__)


class DataProviderOwnerRequired(exc.FaroApiException):
    code = 409
    information = "DataProvider owner required"


class DataProviderNameRequired(exc.FaroApiException):
    code = 409
    information = "DataProvider name required"


class DataProviderApi(common.BaseApi):
    def __init__(self):
        super(DataProviderApi, self).__init__()
        self.base_resource = dps_model.DataProvider
        self.alternate_key = "username"

    def _configure_endpoint(self):
        mod = flask.Blueprint('dps', __name__)

        dps_view = self.as_view('dataprovider_api')
        mod.add_url_rule('/users/<string:userid>/dataproviders',
                         defaults={'id': None},
                         view_func=dps_view,
                         methods=['GET', 'OPTIONS', 'POST'])
        mod.add_url_rule('/dataproviders',
                         defaults={'id': None, 'userid': None},
                         view_func=dps_view, methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/dataproviders',
                         defaults={'userid': None},
                         view_func=dps_view, methods=['POST', 'OPTIONS'])
        mod.add_url_rule('/dataproviders/<id>', view_func=dps_view,
                         methods=['GET', 'OPTIONS'])
        mod.add_url_rule('/dataproviders/<id>', view_func=dps_view,
                         defaults={'userid': None},
                         methods=['DELETE', 'PUT', 'OPTIONS'])
        self.blueprint = mod

    def get(self, id, userid, **kwargs):
        self.add_owner_filter(userid)
        return super(DataProviderApi, self).get(id, with_owner=True)

    def put(self, id, userid):
        data = flaskutils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        owner_required = 'owner_id' in data
        self.attach_owner(userid, required=owner_required)
        return super(DataProviderApi, self).put(id, with_owner=True)

    def delete(self, id, userid):
        return super(DataProviderApi, self).delete(id)

    @flaskutils.require_body
    def post(self, userid):
        data = flaskutils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        self.attach_owner(userid)
        try:
            return super(DataProviderApi, self).post(with_owner=True)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise DataProviderNameRequired()
