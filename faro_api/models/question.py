import sqlalchemy as sa
#import sqlalchemy.orm as orm

import faro_api.models.item as item
import faro_api.utils as utils


class Question(item.Item):
    id = sa.Column(sa.Unicode(36), sa.ForeignKey('items.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'question',
    }

    def __init__(self, **kwargs):
        super(Question, self).__init__(**kwargs)
        self.id = unicode(utils.make_uuid())

    @staticmethod
    def query_columns():
        return item.Item.query_columns()

    def read_only_columns(self):
        return super(Question, self).read_only_columns()

    def to_dict(self, with_owner=False):
        return super(Question, self).to_dict()