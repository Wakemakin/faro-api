import json

from flask import Blueprint, request, jsonify, Response
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from faro_api import app
from faro_api.database import db_session
from faro_api.models import Event
from faro_api.utils import is_uuid
from faro_api.exceptions import common as exc


class EventApi(MethodView):

    def get(self, event_id):
        if event_id is None:
            res = list()
            events = Event.query.all()
            if events is not None:
                for event in events:
                    res.append(event.to_dict())
            return jsonify(objects=res), 200, {}
        try:
            if is_uuid(event_id):
                event = Event.query.filter(Event.id == event_id).one()
            else:
                event = Event.query.filter(Event.name == event_id).one()
            return jsonify(objects=event.to_dict()), 200, {}
        except NoResultFound:
            raise exc.NotFound()

    def post(self):
        data = json.loads(request.data)
        try:
            event = Event(**data)
            db_session.add(event)
            db_session.commit()
            return jsonify(objects=event.to_dict()), 201, {}
        except TypeError as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.InvalidInput
        except Exception as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.UnknownError()

    def delete(self, event_id):
        try:
            if is_uuid(event_id):
                event = Event.query.filter(Event.id == event_id).one()
            else:
                event = Event.query.filter(Event.name == event_id).one()
            db_session.delete(event)
            db_session.commit()
            return Response(status=204)
        except NoResultFound:
            raise exc.NotFound()
        except Exception as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.UnknownError()


mod = Blueprint('events', __name__, url_prefix='/api/events')

event_view = EventApi().as_view('event_api')
mod.add_url_rule('', defaults={'event_id': None},
                 view_func=event_view, methods=['GET'])
mod.add_url_rule('', view_func=event_view, methods=['POST'])
mod.add_url_rule('/<event_id>', view_func=event_view,
                 methods=['GET', 'DELETE'])
