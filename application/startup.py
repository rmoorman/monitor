from os import path


def init_app(app, db, extra_config={}):

    app.config.from_object('config')
    app.config.update(extra_config)

    from application import models, service, auth, rest, forms, views

    if not app.testing and not path.exists(app.config['DATABASE']):
        db.create_all()
