import sqlalchemy as sa
import sqlalchemy.orm as orm

import faro_api.database as db
import faro_common.utils as utils


class Event(db.model()):
    id = sa.Column(sa.Unicode(36), primary_key=True)
    name = sa.Column(sa.Unicode(32), nullable=False)
    description = sa.Column(sa.Unicode(128), nullable=True)
    is_template = sa.Column(sa.Boolean, default=False)
    parent_id = sa.Column(sa.Unicode(36), sa.ForeignKey('events.id'))
    backref = orm.backref('parent', remote_side=[id])
    children = orm.relationship('Event', backref=backref)
    owner_id = sa.Column(sa.Unicode(36), sa.ForeignKey('users.id'),
                         nullable=False)
    backref = orm.backref('events', cascade='all,delete')
    owner = orm.relationship('User', backref=backref)

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
