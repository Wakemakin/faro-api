import json

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from faro_api import app
from faro_api.database import db_session
from faro_api.models import User
from faro_api.utils import is_uuid
from faro_api.exceptions import common as exc


def _make_user_dict(user):
    return {"username": user.username,
            "id": user.id}


mod = Blueprint('users', __name__, url_prefix='/api/users')


@mod.route('/<userid>', methods=['GET'])
@mod.route('', methods=['GET', 'POST'])
def index(userid=None):
    if request.method == 'GET':
        if userid is not None:
            try:
                if is_uuid(userid):
                    user = User.query.filter(User.id == userid).one()
                else:
                    user = User.query.filter(User.username == userid).one()
                return jsonify(objects=_make_user_dict(user))
            except NoResultFound:
                raise exc.NotFound()

        res = list()
        users = User.query.all()
        if users is not None:
            for user in users:
                res.append(_make_user_dict(user))
        return jsonify(objects=res)

    if request.method == 'POST':
        data = json.loads(request.data)
        try:
            user = User(data['username'])
            db_session.add(user)
            db_session.commit()
            return jsonify(objects=_make_user_dict(user)), 201
        except IntegrityError as e:
            app.logger.error(e)
            raise UniqueUsernameRequired()
        except Exception as e:
            app.logger.error(e)
            db_session.rollback()
            raise exc.UnknownError()

    raise exc.UnknownError()


class UniqueUsernameRequired(exc.FaroException):
    code = 409
    information = "Username must be unique"
