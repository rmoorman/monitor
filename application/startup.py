from os import path

from application import app, db


def init_app():

    app.config.from_object('config')

    from application import (
        auth,
        models,
        service,
        conc,
        rest,
        forms,
        feeds,
        views
    )

    if not app.testing and not path.exists(app.config['DATABASE']):
        db.create_all()

    return(app)
