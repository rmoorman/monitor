from flask import request, Response
from functools import wraps
from random import choice

from application import app


def check_auth(username, password):
    return app.config['USERNAME'] and username == app.config['USERNAME'] and \
        app.config['PASSWORD'] and password == app.config['PASSWORD']


def ask_auth():
    return Response(
        '{} - Bitte zuerst einloggen\n'.format(choice([
            'Das geht so nicht.',
            'Das ist Falsch!',
            'Obacht',
            'So nicht!',
            'Um Himmels willen, nein!'
        ])),
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return ask_auth()
        return f(*args, **kwargs)
    return decorated
