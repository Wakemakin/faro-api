from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from faro_api import app
from faro_api import utils
from faro_api.exceptions import common as exc
from faro_api.models.base_models import Base

default_engine = create_engine(app.config['DATABASE_URI'],
                               convert_unicode=True,
                               **app.config['DATABASE_CONNECT_OPTIONS'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=default_engine))


def get_one(cls, filter_value, alternative_check=None):
    if utils.is_uuid(filter_value):
        return cls.query.filter(cls.id == filter_value).one()
    elif alternative_check is not None:
        alt_col = getattr(cls, alternative_check)
        return cls.query.filter(alt_col == filter_value).one()
    raise exc.NotFound()


Model = declarative_base(cls=Base)
Model.query = db_session.query_property()


def init_db(engine=None):
    if engine is None:
        engine = default_engine
    from faro_api.models import user, event
    Model.metadata.create_all(bind=engine)
