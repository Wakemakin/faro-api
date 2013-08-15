import sqlalchemy as sa
import sqlalchemy.orm as orm

import faro_api.database as db
import faro_common.utils as utils

class Role(db.model()):
    id = sa.Column(sa.Unicode(36), primary_key=True)
    name = sa.Column(sa.Unicode(32), unique=True, nullable=False)
    
    users = orm.relationship('users',backref='roles', secondary = users_roles)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())
        self.name = kwargs['name'].lower()

    @staticmethod
    def read_only_columns():
        return ['name']

    @staticmethod
    def query_columns():
        return ['name']

    def to_dict(self, with_events=False):
        ret = {'name': self.name,
               'date_created': str(self.date_created)}
        return ret
