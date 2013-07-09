from sqlalchemy import Column, Boolean, Unicode, ForeignKey
from sqlalchemy.orm import relationship, backref

import faro_api.database as db
from faro_api.utils import make_uuid


class Event(db.model()):
    id = Column(Unicode, primary_key=True)
    name = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=True)
    is_template = Column(Boolean, default=False)
    parent_id = Column(Unicode, ForeignKey('events.id'))
    children = relationship('Event',
                            backref=backref('parent', remote_side=[id]))
    owner_id = Column(Unicode, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', backref=backref('events'))

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.id = unicode(make_uuid())

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
