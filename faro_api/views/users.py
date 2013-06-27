import json

from flask import Blueprint, request, jsonify, Response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from faro_api import app
from faro_api.database import db_session
from faro_api.models import User
from faro_api.utils import is_uuid
from faro_api.exceptions import common as exc


class UniqueUsernameRequired(exc.FaroException):
    code = 409
    information = "Username must be unique"


class UserApi(MethodView):
    def _make_user_dict(self, user):
        return {"username": user.username,
                "id": user.id}

    def get(self, user_id):
        if user_id is None:
            res = list()
            users = User.query.all()
            if users is not None:
                for user in users:
                    res.append(self._make_user_dict(user))
            return jsonify(objects=res), 200, {}
        try:
            if is_uuid(user_id):
                user = User.query.filter(User.id == user_id).one()
            else:
                user = User.query.filter(User.username == user_id).one()
            return jsonify(objects=self._make_user_dict(user)), 200, {}
        except NoResultFound:
            raise exc.NotFound()

    def post(self):
        data = json.loads(request.data)
        try:
            user = User(data['username'])
            db_session.add(user)
            db_session.commit()
            return jsonify(objects=self._make_user_dict(user)), 201, {}
        except IntegrityError as e:
            app.logger.error(e)
            raise UniqueUsernameRequired()
        except Exception as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.UnknownError()

    def delete(self, user_id):
        try:
            if is_uuid(user_id):
                user = User.query.filter(User.id == user_id).one()
            else:
                user = User.query.filter(User.username == user_id).one()
            db_session.delete(user)
            db_session.commit()
            return Response(status=204)
        except NoResultFound:
            raise exc.NotFound()
        except Exception as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.UnknownError()


mod = Blueprint('users', __name__, url_prefix='/api/users')

user_view = UserApi().as_view('user_api')
mod.add_url_rule('', defaults={'user_id': None},
                 view_func=user_view, methods=['GET'])
mod.add_url_rule('', view_func=user_view, methods=['POST'])
mod.add_url_rule('/<user_id>', view_func=user_view,
                 methods=['GET', 'DELETE'])
