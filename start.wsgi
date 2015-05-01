#!./venv/bin/python3

activate = '/srv/monitor/venv/bin/activate_this.py'

exec(
    compile(
        open(activate, 'rb').read(),
        activate,
        'exec'
    ),
    dict(
        __file__=activate
    )
)

from sys import path as _spath

_spath.insert(0, '/srv/monitor')

from application.startup import init_app

application = init_app()
