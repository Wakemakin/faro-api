from datetime import datetime

from sqlalchemy import Column, Boolean, Unicode, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from faro_api.database import Model
from faro_api.utils import make_uuid


class User(Model):
    __tablename__ = 'users'
    id = Column(Unicode, primary_key=True)
    username = Column(Unicode, unique=True)

    def __init__(self, username, **kwargs):
        super(User, self).__init__(**kwargs)
        self.id = unicode(make_uuid())
        self.date_created = datetime.now()
        self.username = username


class Event(Model):
    __tablename__ = 'events'
    id = Column(Unicode, primary_key=True)
    name = Column(Unicode)
    description = Column(Unicode, nullable=True)
    date_created = Column(DateTime)
    is_template = Column(Boolean, default=False)
    parent_id = Column(Unicode, ForeignKey('events.id'))
    children = relationship('Event',
                            backref=backref('parent', remote_side=[id]))
    owner_id = Column(Unicode, ForeignKey('users.id'))
    owner = relationship('User', backref=backref('events'))

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.id = unicode(make_uuid())
        self.date_created = datetime.now()
