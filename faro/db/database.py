def init_db(engine=None):
    import models
    return models.make_session(engine=engine)
