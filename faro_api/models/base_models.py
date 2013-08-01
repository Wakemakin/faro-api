import logging

import sqlalchemy as sa
import sqlalchemy.ext.declarative as decl

from faro_common.exceptions import common as exc

logger = logging.getLogger("faro_api."+__name__)


class Base(object):
    _read_only_base = ['id', 'date_created']

    @decl.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    date_created = sa.Column(sa.DateTime, default=sa.func.now())

    def __init__(self, **kwargs):
        pass

    def to_dict(self):
        pass

    def read_only_columns(self):
        return []

    def query_columns(self):
        return []

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self._read_only_base or\
                    key in self.read_only_columns():
                raise exc.Forbidden(information="%s is read-only" % key)
            if not hasattr(self, key):
                raise exc.InvalidInput(information="%s is invalid" % key)
            setattr(self, key, value)
