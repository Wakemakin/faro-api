from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, DateTime
from faro_api import app

from faro_api.exceptions import common as exc

engine = create_engine(app.config['DATABASE_URI'],
                       convert_unicode=True,
                       **app.config['DATABASE_CONNECT_OPTIONS'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


def init_db():
    Model.metadata.create_all(bind=engine)


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


Model = declarative_base(cls=Base)
Model.query = db_session.query_property()

from faro_api import models

#event.listen(db_session, 'after_flush', search.update_model_based_indexes)
