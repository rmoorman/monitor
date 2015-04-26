from os import path

from application import app, db


def init_app():

    app.config.from_object('config')

    from application import models, service, auth, rest, forms, views

    if not app.testing and not path.exists(app.config['DATABASE']):
        db.create_all()

    return(app)
