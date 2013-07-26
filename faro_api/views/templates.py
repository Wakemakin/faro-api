import logging

import flask
import sqlalchemy.exc
import sqlalchemy.orm.exc as sa_exc

from faro_api import database as db
from faro_api.exceptions import common as exc
from faro_api.models import template as template_model
from faro_api.models import user as user_model
from faro_api import utils
from faro_api.views import common

logger = logging.getLogger('faro_api.'+__name__)


class TemplateApi(common.BaseApi):
    def __init__(self):
        super(TemplateApi, self).__init__()
        self.base_resource = template_model.Template

    def _configure_endpoint(self):
        mod = flask.Blueprint('templates', __name__)

        template_view = self.as_view('template_api')
        mod.add_url_rule('/templates', defaults={'userid': None},
                         view_func=template_view, methods=['POST'])
        mod.add_url_rule('/users/<string:userid>/templates',
                         view_func=template_view, methods=['POST'])

        mod.add_url_rule('/users/<string:userid>/templates',
                         defaults={'id': None},
                         view_func=template_view, methods=['GET'])
        mod.add_url_rule('/templates', defaults={'id': None,
                         'userid': None},
                         view_func=template_view, methods=['GET'])

        mod.add_url_rule('/templates/<id>', view_func=template_view,
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
            return super(TemplateApi, self).get(id, with_owner=True)
        else:
            user_id = userid
            try:
                user = db.get_one(session, user_model.User, user_id,
                                  "username")
                self.additional_filters['owner_id'] = user.id
            except sa_exc.NoResultFound:
                raise exc.NotFound()
            return super(TemplateApi, self).get(id, with_owner=True)
        raise exc.NotFound()

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
        return super(TemplateApi, self).put(id, with_owner=with_owner,
                                            attachments=attachments)

    def delete(self, id, userid):
        return super(TemplateApi, self).delete(id)

    @utils.require_body
    def post(self, userid):
        session = flask.g.session
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        with_owner = False
        attachments = None
        user_id = None
        if 'owner_id' in data:
            user_id = data['owner_id']
        if userid is not None:
            user_id = userid
        if user_id is not None:
            try:
                user = db.get_one(session, user_model.User,
                                  user_id, "username")
                data['owner_id'] = user.id
                attachments = {'owner': user}
                with_owner = True
            except sa_exc.NoResultFound:
                raise exc.NotFound(information="Owner not found")
        try:
            return super(TemplateApi, self).post(with_owner=with_owner,
                                                 attachments=attachments)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise exc.InvalidInput()
