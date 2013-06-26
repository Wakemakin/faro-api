from datetime import datetime
import uuid

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm as orm



Base = declarative_base()

def make_session(engine=None):
    if not engine:
        engine = db.create_engine('sqlite:////tmp/tmp.db',
                                  convert_unicode=True)
    else:
        engine = db.create_engine(engine,
                                  convert_unicode=True)

    Base.metadata.bind = engine
    Base.metadata.create_all()
    Session = orm.sessionmaker(autocommit=False, autoflush=False,
                               bind=engine)
    return orm.scoped_session(Session)


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Unicode, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    date_created = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.id = unicode(uuid.uuid1())
        self.date_created = datetime.now()

class Event(Base):
    __tablename__ = 'events'
    id = db.Column(db.Unicode, primary_key=True)
    name = db.Column(db.Unicode)
    description = db.Column(db.Unicode, nullable=True)
    date_created = db.Column(db.DateTime)
    is_template = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Unicode, db.ForeignKey('events.id'))
    children = orm.relationship("Event",
            backref=orm.backref('parent', remote_side=[id])
            )
    owner_id = db.Column(db.Unicode, db.ForeignKey('users.id'))
    owner = orm.relationship('User', backref=orm.backref('events'))
    
    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.id = unicode(uuid.uuid1())
        self.date_created = datetime.now()

class Choice(Base):
    __tablename__ = 'choices'
    id = db.Column(db.Unicode, primary_key=True)
    name = db.Column(db.Unicode)
    date_created = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(Choice, self).__init__(**kwargs)
        self.id = unicode(uuid.uuid1())
        self.date_created = datetime.now()
