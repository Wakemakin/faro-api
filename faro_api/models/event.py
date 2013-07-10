import sqlalchemy as sa
import sqlalchemy.orm as orm

import faro_api.database as db
import faro_api.utils as utils


class Event(db.model()):
    id = sa.Column(sa.Unicode, primary_key=True)
    name = sa.Column(sa.Unicode, nullable=False)
    description = sa.Column(sa.Unicode, nullable=True)
    is_template = sa.Column(sa.Boolean, default=False)
    parent_id = sa.Column(sa.Unicode, sa.ForeignKey('events.id'))
    backref = orm.backref('parent', remote_side=[id])
    children = orm.relationship('Event', backref=backref)
    owner_id = sa.Column(sa.Unicode, sa.ForeignKey('users.id'), nullable=False)
    owner = orm.relationship('User', backref=orm.backref('events'))

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())

    @staticmethod
    def query_columns():
        return ['name',
                'owner_id',
                'is_template']

    def read_only_columns(self):
        return []

    def to_dict(self, with_owner=False):
        ret = {'name': self.name,
               'id': self.id,
               'owner_id': self.owner_id,
               'parent_id': self.parent_id,
               'is_template': self.is_template,
               'description': self.description,
               'owner': None,
               'date_created': str(self.date_created)}
        if with_owner and self.owner is not None:
            ret['owner'] = self.owner.to_dict()
        return ret
