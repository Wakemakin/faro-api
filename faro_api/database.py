from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, DateTime

from faro_api import utils as utils
from faro_api.exceptions import common as exc


@utils.static_var("instance", None)
def model():
    if model.instance is None:
        model.instance = declarative_base(cls=Base)
    return model.instance


def create_db_environment(app):
    engine = create_engine(app.config['DATABASE_URI'],
                           convert_unicode=True,
                           **app.config['DATABASE_CONNECT_OPTIONS'])
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))

    @app.teardown_request
    def remove_db_session(exception):
        db_session.remove()
        db_session.close()

    from faro_api.models import user
    from faro_api.models import event
    [user, event]
    model().metadata.create_all(bind=engine)

    return db_session


def get_one(session, cls, filter_value, alternative_check=None):
    if utils.is_uuid(filter_value):
        return session.query(cls).filter(cls.id == filter_value).one()
    elif alternative_check is not None:
        alt_col = getattr(cls, alternative_check)
        return session.query(cls).filter(alt_col == filter_value).one()
    raise exc.NotFound()


class Base(object):
    _read_only_base = ['id', 'date_created']

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    date_created = Column(DateTime, default=func.now())

    def __init__(self, **kwargs):
        pass

    def to_dict(self):
        pass

    def read_only_columns(self):
        return []

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self._read_only_base or\
                    key in self.read_only_columns():
                raise exc.Forbidden(information="%s is read-only" % key)
            if not hasattr(self, key):
                raise exc.InvalidInput(information="%s is invalid" % key)
            setattr(self, key, value)
