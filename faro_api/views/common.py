import logging

import flask
import flask.ext.jsonpify as jsonp
import flask.views as views
import sqlalchemy.orm.exc as sa_exc

from faro_api import database as db
from faro_api.exceptions import common as f_exc
from faro_common.exceptions import common as exc
from faro_common import flask as flaskutils

logger = logging.getLogger('faro_api.'+__name__)


class BaseApi(views.MethodView):
    def __init__(self):
        self.base_resource = None
        self.alternate_key = None
        self._configure_endpoint()
        self.additional_filters = {}
        self.attachments = {}

    def attach_event(self, event_id, required=True):
        event, id = db.get_event(event_id)
        logger.debug(event_id)
        if required and event is None:
            if id is None:
                raise f_exc.EventRequired()
            if id is not None:
                raise exc.NotFound()
        if event is not None:
            self.attachments['event'] = event
            return event
        return None

    def attach_owner(self, owner_id, required=True):
        user, id = db.get_owner(owner_id)
        if required and user is None:
            if id is None:
                raise f_exc.OwnerRequired()
            if id is not None:
                raise exc.NotFound()
        if user is not None:
            self.attachments['owner'] = user
            return user
        return None

    def add_event_filter(self, event_id):
        event, id = db.get_event(event_id)
        if event is not None:
            self.additional_filters['event_id'] = event.id

    def add_owner_filter(self, owner_id):
        user, id = db.get_owner(owner_id)
        if user is not None:
            self.additional_filters['owner_id'] = user.id

    @flaskutils.crossdomain(origin='*')
    def options(self, id, eventid):
        return flask.current_app.make_default_options_response()

    @flaskutils.crossdomain(origin='*')
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

    @flaskutils.require_body
    @flaskutils.crossdomain(origin='*')
    def post(self, **kwargs):
        session = flask.g.session
        data = flaskutils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        try:
            result = self.base_resource(**data)
            for attach, value in self.attachments.items():
                logger.debug(attach)
                setattr(result, attach, value)
            session.add(result)
            session.commit()
            return jsonp.jsonify(result.to_dict(**kwargs)), 201, {}
        except TypeError as e:
            logger.error(e)
            session.rollback()
            raise exc.InvalidInput

    @flaskutils.require_body
    @flaskutils.crossdomain(origin='*')
    def put(self, id, **kwargs):
        session = flask.g.session
        data = flaskutils.json_request_data(flask.request.data)
        if not data:
            raise exc.RequiresBody()
        try:
            result = db.get_one(session, self.base_resource, id,
                                self.alternate_key)
            for attach, value in self.attachments.items():
                setattr(result, attach, value)
            result.update(**data)
            session.commit()
            return jsonp.jsonify(result.to_dict(**kwargs)), 200, {}
        except sa_exc.NoResultFound:
            raise exc.NotFound()

    @flaskutils.crossdomain(origin='*')
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
