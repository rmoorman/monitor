#!/usr/bin/env python3

from application.startup import init_app

app = init_app()

if __name__ == '__main__':
    app.run(
        '::1',
        # '::',
        # '127.0.0.1',
        # '0.0.0.0',
        port=5000,
        debug=True
    )
