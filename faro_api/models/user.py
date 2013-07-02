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

    def to_dict(self, with_events=False):
        ret = {'username': self.username,
               'id': self.id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'date_created': str(self.date_created)}
        if with_events:
            ret['events'] = [event.to_dict() for event in self.events]
        return ret
