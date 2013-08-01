import sqlalchemy as sa
import sqlalchemy.orm as orm

import faro_api.database as db
import faro_common.utils as utils


class DataProvider(db.model()):
    id = sa.Column(sa.Unicode(36), primary_key=True)
    description = sa.Column(sa.Unicode(128), nullable=True)
    name = sa.Column(sa.Unicode(32), nullable=False)
    public = sa.Column(sa.Boolean, default=False)
    owner_id = sa.Column(sa.Unicode(36), sa.ForeignKey('users.id'),
                         nullable=False)
    backref = orm.backref('dataproviders', cascade='all,delete')
    owner = orm.relationship('User', backref=backref)

    def __init__(self, **kwargs):
        super(DataProvider, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())

    @staticmethod
    def read_only_columns():
        return []

    @staticmethod
    def query_columns():
        return []

    def to_dict(self, with_owner=False):
        ret = {'name': self.name,
               'description': self.description,
               'id': self.id,
               'owner_id': self.owner_id,
               'public': self.public,
               'date_created': str(self.date_created)}
        if with_owner and self.owner is not None:
            ret['owner'] = self.owner.to_dict()
        return ret
