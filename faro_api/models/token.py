import sqlalchemy as sa
import sqlalchemy.orm as orm

import faro_api.database as db
import faro_common.utils as utils


class Token(db.model()):
    id = sa.Column(sa.Unicode(36), primary_key=True)
    owner_id = sa.Column(sa.Unicode(36), sa.ForeignKey('users.id'),
                         nullable=False)
    backref = orm.backref('tokens', cascade='all,delete')
    owner = orm.relationship('User', backref=backref)

    def __init__(self, **kwargs):
        super(Token, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())

    @staticmethod
    def read_only_columns():
        return []

    @staticmethod
    def query_columns():
        return ['owner_id']

    def to_dict(self, with_owner=False):
        ret = {'id': self.id,
               'owner_id': self.owner_id}
        if with_owner:
            ret['owner'] = self.owner.to_dict()
        return ret
