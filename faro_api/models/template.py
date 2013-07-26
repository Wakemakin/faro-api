import sqlalchemy as sa
import sqlalchemy.orm as orm

import faro_api.database as db
import faro_api.utils as utils


class Template(db.model()):
    id = sa.Column(sa.Unicode(36), primary_key=True)
    title = sa.Column(sa.Unicode(32), nullable=False)
    template_type = sa.Column(sa.Unicode(32), nullable=False)
    description = sa.Column(sa.Unicode(128), nullable=True)
    owner_id = sa.Column(sa.Unicode(36), sa.ForeignKey('users.id'),
                         nullable=True)
    owner = orm.relationship('User', backref=orm.backref('templates'))

    def __init__(self, **kwargs):
        super(Template, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())

    @staticmethod
    def read_only_columns():
        return ['template_type']

    @staticmethod
    def query_columns():
        return ['title',
                'owner_id',
                'template_type',
                'date_created']

    def to_dict(self, with_owner=False):
        ret = {'title': self.title,
               'id': self.id,
               'description': self.description,
               'template_type': self.template_type,
               'owner': None,
               'date_created': str(self.date_created)}
        if with_owner and self.owner is not None:
            ret['owner'] = self.owner.to_dict()
        return ret
