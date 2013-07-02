from sqlalchemy import Column, Boolean, Unicode, ForeignKey
from sqlalchemy.orm import relationship, backref

from faro_api.database import Model
from faro_api.utils import make_uuid


class User(Model):
    id = Column(Unicode, primary_key=True)
    username = Column(Unicode, unique=True)
    first_name = Column(Unicode)
    last_name = Column(Unicode)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.id = unicode(make_uuid())

    def read_only_columns(self):
        return ['username']

    def to_dict(self):
        return {'username': self.username,
                'id': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'date_created': str(self.date_created)}


class Event(Model):
    id = Column(Unicode, primary_key=True)
    name = Column(Unicode)
    description = Column(Unicode, nullable=True)
    is_template = Column(Boolean, default=False)
    parent_id = Column(Unicode, ForeignKey('events.id'))
    children = relationship('Event',
                            backref=backref('parent', remote_side=[id]))
    owner_id = Column(Unicode, ForeignKey('users.id'))
    owner = relationship('User', backref=backref('events'))

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.id = unicode(make_uuid())

    def read_only_columns(self):
        return []

    def to_dict(self):
        return {'name': self.name,
                'id': self.id,
                'description': self.description,
                'date_created': str(self.date_created)}
