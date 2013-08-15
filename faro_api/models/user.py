import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as decl

import faro_api.database as db
import faro_common.utils as utils

saBase = decl.declarative_base()

users_roles = sa.Table(
    'user_roles', 
    saBase.metadata,
    sa.Column('fk_user', sa.Unicode(36), sa.ForeignKey('users.id')),
    sa.Column('fk_role', sa.Unicode(36), sa.ForeignKey('roles.id'))
)

class User(db.model()):
    id = sa.Column(sa.Unicode(36), primary_key=True)
    username = sa.Column(sa.Unicode(32), unique=True, nullable=False)
    display_name = sa.Column(sa.Unicode(32), unique=True, nullable=False)
    first_name = sa.Column(sa.Unicode(32))
    last_name = sa.Column(sa.Unicode(32))

    roles = orm.relationship('roles',backref='users', secondary = users_roles)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())
        self.display_name = kwargs['username']
        self.username = kwargs['username'].lower()

    @staticmethod
    def has_owner(self):
        return False

    @staticmethod
    def read_only_columns():
        return ['username']

    @staticmethod
    def query_columns():
        return ['first_name',
                'last_name',
                'date_created']

    def to_dict(self, with_events=False):
        ret = {'username': self.username,
               'display_name': self.display_name,
               'id': self.id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'date_created': str(self.date_created)}
        if with_events:
            ret['events'] = [event.to_dict() for event in self.events]
        return ret
