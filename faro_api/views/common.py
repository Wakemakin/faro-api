import logging

from flask import jsonify, Response, request, g
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from faro_api.exceptions import common as exc
from faro_api import database as db
from faro_api import utils

logger = logging.getLogger('faro_api.'+__name__)


class BaseApi(MethodView):
    def __init__(self):
        self.base_resource = None
        self.alternate_key = None
        self._configure_endpoint()

    def _configure_endpoint(self):
        pass

    def get(self, id, **kwargs):
        session = g.session
        filters = request.args
        q = session.query(self.base_resource)
        if id is None:
            res = list()
            if len(filters):
                q = db.create_filters(q, self.base_resource, filters)
            total = q.count()
            q, output = db.handle_paging(q, filters, total, request.url)
            results = q.all()
            if results is not None:
                for result in results:
                    res.append(result.to_dict(**kwargs))
            return jsonify(objects=res, **output), 200, {}
        try:
            result = db.get_one(session, self.base_resource, id,
                                self.alternate_key)
            return jsonify(objects=result.to_dict(**kwargs),
                           paging={"total": 100}), 200, {}
        except NoResultFound:
            raise exc.NotFound()

    @utils.require_body
    def post(self, **kwargs):
        session = g.session
        data = utils.json_request_data(request.data)
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
            return jsonify(result.to_dict(**kwargs)), 201, {}
        except TypeError as e:
            logger.error(e)
            session.rollback()
            raise exc.InvalidInput

    @utils.require_body
    def put(self, id, **kwargs):
        session = g.session
        data = utils.json_request_data(request.data)
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
            return jsonify(result.to_dict(**kwargs)), 200, {}
        except NoResultFound:
            raise exc.NotFound()

    def delete(self, id):
        session = g.session
        try:
            result = db.get_one(session, self.base_resource, id,
                                self.alternate_key)
            session.delete(result)
            session.commit()
            return Response(status=204)
        except NoResultFound:
            raise exc.NotFound()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise exc.UnknownError()
