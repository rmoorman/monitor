#!/usr/bin/env python3

from application import app, db
from application.startup import init_app

init_app(app, db)

if __name__ == '__main__':
    app.run(
        '::1',
        # '127.0.0.1',
        port=5000,
        debug=True
    )
