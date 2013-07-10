import sqlalchemy as sa

import faro_api.database as db
import faro_api.utils as utils


class User(db.model()):
    id = sa.Column(sa.Unicode, primary_key=True)
    username = sa.Column(sa.Unicode, unique=True)
    first_name = sa.Column(sa.Unicode)
    last_name = sa.Column(sa.Unicode)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())

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
               'id': self.id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'date_created': str(self.date_created)}
        if with_events:
            ret['events'] = [event.to_dict() for event in self.events]
        return ret
