import sqlalchemy as sa
import sqlalchemy.orm as orm

import faro_api.database as db
import faro_common.utils as utils


class Item(db.model()):
    id = sa.Column(sa.Unicode(36), primary_key=True)
    type = sa.Column(sa.String(16))
    name = sa.Column(sa.Unicode(32), nullable=False)
    description = sa.Column(sa.Unicode(128), nullable=True)
    event_id = sa.Column(sa.Unicode(36), sa.ForeignKey('events.id'))
    backref = orm.backref('items', cascade='all,delete')
    event = orm.relationship('Event', backref=backref)

    owner_id = sa.Column(sa.Unicode(36), sa.ForeignKey('users.id'),
                         nullable=False)
    backref = orm.backref('items', cascade='all,delete')
    owner = orm.relationship('User', backref=backref)

    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())

    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': type
    }

    @staticmethod
    def query_columns():
        return ['name', 'owner_id']

    def read_only_columns(self):
        return []

    def to_dict(self):
        ret = {'name': self.name, 'id': self.id,
               'description': self.description,
               'owner_id': self.owner_id,
               'event_id': self.event_id,
               'date_created': str(self.date_created)}
        return ret
