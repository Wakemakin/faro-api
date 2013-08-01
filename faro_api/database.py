import flask
import logging
import urllib
import urlparse

import sqlalchemy as sa
import sqlalchemy.engine
import sqlalchemy.ext.declarative as decl
import sqlalchemy.orm as orm
import sqlite3

from faro_common import decorators as dec
from faro_common.exceptions import common as exc
from faro_common import flask as flask_utils
from faro_common import utils as utils


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
    [user, event, item, question, action, dataprovider]
    model().metadata.create_all(bind=engine)

    return db_session


def get_object(key, object_type, filter_key, alternate_key_column=None):
    import sqlalchemy.orm.exc as sa_exc
    session = flask.g.session
    filters = flask.request.args
    data = None
    try:
        data = flask_utils.json_request_data(flask.request.data)
    except exc.InvalidInput:
        pass
    found_id = None
    if key is not None:
        found_id = key
    elif data is not None and filter_key in data:
        found_id = data[filter_key]
    elif filter_key in filters:
        found_id = filters.getlist(filter_key)[0]

    if found_id is None and key is None:
        return None, None

    try:
        if alternate_key_column is not None:
            obj = get_one(session, object_type, found_id,
                          alternate_key_column)
        else:
            obj = get_one(session, object_type, found_id)
        return obj, found_id
    except sa_exc.NoResultFound:
        raise exc.NotFound()


def get_owner(userid):
    from faro_api.models import user
    return get_object(userid, user.User, 'owner_id',
                      alternate_key_column='username')


def get_event(eventid):
    from faro_api.models import event
    return get_object(eventid, event.Event, 'event_id')


def get_one(session, cls, filter_value, alternative_check=None):
    if utils.is_uuid(filter_value):
        return session.query(cls).filter(cls.id == filter_value).one()
    elif alternative_check is not None:
        alt_col = getattr(cls, alternative_check)
        filter_value = filter_value.lower()
        return session.query(cls).filter(alt_col == filter_value).one()
    raise exc.InvalidInput()


def create_filters(query, cls, filter_list, additional_filters):
    for column in cls.query_columns():
        """Additional_filters overrides query filters"""
        if column in additional_filters:
            value = additional_filters[column]
            query = query.filter(getattr(cls, column) == value)
        elif column in filter_list:
            value = filter_list.getlist(column)[0]
            query = query.filter(getattr(cls, column).
                                 like("%%%s%%" % value))
    return query


def handle_paging(query, filters, total, url):
    page = 1
    page_size = flask.current_app.config['DEFAULT_PAGE_SIZE']
    if 'p' in filters:
        page = filters.get('p', type=int)
    if 'page_size' in filters:
        page_size = filters.get('page_size', type=int)
    if page_size > flask.current_app.config['MAXIMUM_PAGE_SIZE']:
        page_size = flask.current_app.config['MAXIMUM_PAGE_SIZE']
    page_total = page_size * (page - 1)
    if page <= 0 or page_total > total:
        raise exc.NotFound()
    output = {'total': total, 'page_number': page, 'page_size': page_size}
    o = urlparse.urlsplit(url)
    if len(o.query) > 0:
        if 'p' in filters:
            if page > 1:
                qs = urlparse.parse_qsl(o.query)
                qs = urllib.urlencode([(name, int(value) - 1
                                      if name == 'p' else value)
                                      for name, value in qs])
                new_url = urlparse.urlunsplit([o.scheme, o.netloc, o.path,
                                               qs, o.fragment])
                output['prev'] = new_url
            if total > page_size and page * page_size < total:
                qs = urlparse.parse_qsl(o.query)
                qs = urllib.urlencode([(name, int(value) + 1
                                      if name == 'p' else value)
                                      for name, value in qs])
                new_url = urlparse.urlunsplit([o.scheme, o.netloc, o.path,
                                               qs, o.fragment])
                output['next'] = new_url
        else:
            if total > page_size and page * page_size < total:
                qs = urlparse.parse_qsl(o.query)
                qs.append(('p', page + 1))
                qs = urllib.urlencode(qs)
                new_url = urlparse.urlunsplit([o.scheme, o.netloc, o.path,
                                               qs, o.fragment])
                output['next'] = new_url
            pass
    elif total > page_size:
        output['next'] = url + '?p=2'
    page = page - 1
    return query.slice(page * page_size, page * page_size + page_size), output


class Base(object):
    _read_only_base = ['id', 'date_created']

    @decl.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    date_created = sa.Column(sa.DateTime, default=sa.func.now())

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self._read_only_base or\
                    key in self.read_only_columns():
                raise exc.Forbidden(information="%s is read-only" % key)
            if not hasattr(self, key):
                raise exc.InvalidInput(information="%s is invalid" % key)
            setattr(self, key, value)
