import logging

import flask
import flask.ext.jsonpify as jsonp
import flask.views as views
import sqlalchemy.orm.exc as sa_exc

from faro_api import database as db
from faro_api.exceptions import common as exc
from faro_api import utils

logger = logging.getLogger('faro_api.'+__name__)


class BaseApi(views.MethodView):
    def __init__(self):
        self.base_resource = None
        self.alternate_key = None
        self._configure_endpoint()
        self.additional_filters = {}

    def _configure_endpoint(self):
        pass

    @utils.crossdomain(origin='*')
    def get(self, id, **kwargs):
        session = flask.g.session
        filters = flask.request.args
        q = session.query(self.base_resource)
        if id is None:
            res = list()
            if len(filters) or len(self.additional_filters):
                q = db.create_filters(q, self.base_resource,
                                      filters, self.additional_filters)
            total = q.count()
            q, output = db.handle_paging(q, filters, total, flask.request.url)
            results = q.all()
            if results is not None:
                for result in results:
                    res.append(result.to_dict(**kwargs))
            return jsonp.jsonify(objects=res, **output), 200, {}
        try:
            result = db.get_one(session, self.base_resource, id,
                                self.alternate_key)
            return jsonp.jsonify(object=result.to_dict(**kwargs)), 200, {}
        except sa_exc.NoResultFound:
            raise exc.NotFound()

    @utils.require_body
    @utils.crossdomain(origin='*')
    def post(self, **kwargs):
        session = flask.g.session
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        try:
            result = self.base_resource(**data)
            if "attachments" in kwargs:
                attachments = kwargs["attachments"]
                if attachments is not None:
                    for attach, value in attachments.items():
                        setattr(result, attach, value)
                kwargs.pop("attachments")
            session.add(result)
            session.commit()
            return jsonp.jsonify(result.to_dict(**kwargs)), 201, {}
        except TypeError as e:
            logger.error(e)
            session.rollback()
            raise exc.InvalidInput

    @utils.require_body
    @utils.crossdomain(origin='*')
    def put(self, id, **kwargs):
        session = flask.g.session
        data = utils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        try:
            result = db.get_one(session, self.base_resource, id,
                                self.alternate_key)
            if "attachments" in kwargs:
                attachments = kwargs["attachments"]
                if attachments is not None:
                    for attach, value in attachments.items():
                        setattr(result, attach, value)
                kwargs.pop("attachments")
            result.update(**data)
            session.commit()
            return jsonp.jsonify(result.to_dict(**kwargs)), 200, {}
        except sa_exc.NoResultFound:
            raise exc.NotFound()

    @utils.crossdomain(origin='*')
    def delete(self, id):
        session = flask.g.session
        try:
            result = db.get_one(session, self.base_resource, id,
                                self.alternate_key)
            session.delete(result)
            session.commit()
            return flask.Response(status=204)
        except sa_exc.NoResultFound:
            raise exc.NotFound()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise exc.UnknownError()
