from flask import jsonify, Response, request
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from faro_api import app
from faro_api.exceptions import common as exc
from faro_api.database import db_session, get_one
from faro_api import utils


class BaseApi(MethodView):
    def __init__(self):
        self.base_resource = None
        self.alternate_key = None

    def get(self, id, **kwargs):
        if id is None:
            res = list()
            results = self.base_resource.query.all()
            if results is not None:
                for result in results:
                    res.append(result.to_dict(**kwargs))
            return jsonify(objects=res), 200, {}
        try:
            result = get_one(self.base_resource, id, self.alternate_key)
            return jsonify(objects=result.to_dict(**kwargs)), 200, {}
        except NoResultFound:
            raise exc.NotFound()

    @utils.require_body
    def post(self, **kwargs):
        data = utils.json_request_data(request.data)
        try:
            result = self.base_resource(**data)
            if "attachments" in kwargs:
                attachments = kwargs["attachments"]
                if attachments is not None:
                    for attach, value in attachments.items():
                        setattr(result, attach, value)
                kwargs.pop("attachments")
            db_session.add(result)
            db_session.commit()
            return jsonify(result.to_dict(**kwargs)), 201, {}
        except TypeError as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.InvalidInput

    @utils.require_body
    def put(self, id, **kwargs):
        data = utils.json_request_data(request.data)
        try:
            result = get_one(self.base_resource, id, self.alternate_key)
            result.update(**data)
            db_session.commit()
            return jsonify(result.to_dict(**kwargs)), 201, {}
        except NoResultFound:
            raise exc.NotFound()

    def delete(self, id):
        try:
            result = get_one(self.base_resource, id, self.alternate_key)
            db_session.delete(result)
            db_session.commit()
            return Response(status=204)
        except NoResultFound:
            raise exc.NotFound()
        except Exception as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.UnknownError()
