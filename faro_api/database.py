import logging

import sqlalchemy as sa
import sqlalchemy.engine
import sqlalchemy.ext.declarative as decl
import sqlalchemy.orm as orm
import sqlite3

from faro_common import decorators as dec
from faro_common.exceptions import common as exc
from faro_common.flask import sautils


@sa.event.listens_for(sqlalchemy.engine.Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


logger = logging.getLogger("faro_api."+__name__)


@dec.static_var("instance", None)
def model():
    if model.instance is None:
        model.instance = decl.declarative_base(cls=Base)
    return model.instance


def create_db_environment(app):
    engine = sa.create_engine(app.config['DATABASE_URI'],
                              convert_unicode=True,
                              **app.config['DATABASE_CONNECT_OPTIONS'])
    db_session = orm.scoped_session(orm.sessionmaker(autocommit=False,
                                                     autoflush=False,
                                                     bind=engine))

    @app.teardown_request
    def remove_db_session(exception):
        db_session.remove()
        db_session.close()

    from faro_api.models import action
    from faro_api.models import dataprovider
    from faro_api.models import event
    from faro_api.models import item
    from faro_api.models import question
    from faro_api.models import user
    from faro_api.models import role
    [user, event, item, question, action, dataprovider, role]
    model().metadata.create_all(bind=engine)

    return db_session


def get_owner(userid):
    from faro_api.models import user
    return sautils.get_object(userid, user.User, 'owner_id',
                              alternate_key_column='username')


def get_event(eventid):
    from faro_api.models import event
    return sautils.get_object(eventid, event.Event, 'event_id')


class Base(object):
    _read_only_base = ['id', 'date_created']

    @decl.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    date_created = sa.Column(sa.DateTime, default=sa.func.now())

    def has_owner(self):
        return True

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self._read_only_base or\
                    key in self.read_only_columns():
                raise exc.Forbidden(information="%s is read-only" % key)
            if not hasattr(self, key):
                raise exc.InvalidInput(information="%s is invalid" % key)
            setattr(self, key, value)
