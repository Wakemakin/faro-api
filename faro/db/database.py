from werkzeug.local import LocalProxy

from flask import g

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = init_db()
    return db

def init_db(engine=None):
    import models
    return models.make_session(engine=engine)

db = LocalProxy(get_db)
