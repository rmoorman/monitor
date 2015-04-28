from json import dumps, loads
from os import getenv, mkdir, path
from random import choice
from string import ascii_lowercase, digits


def _rand():
    return ''.join(choice(ascii_lowercase + digits) for _ in range(128))


def _jread(filename):
    if path.exists(filename):
        with open(filename, 'r') as f:
            return loads(f.read())


def _jwrite(filename, content):
    with open(filename, 'w') as f:
        return f.write(dumps(content))


basedir = path.dirname(path.abspath(__file__))

datadir = path.join(basedir, 'data')
if not path.exists(datadir):
    mkdir(datadir)

auth_json = path.join(datadir, 'auth.json')
secret_key_json = path.join(datadir, 'key.json')

auth = _jread(auth_json)
secret_key = _jread(secret_key_json)

if not auth:
    auth = {
        'USERNAME': getenv('MONITORUSER', _rand()),
        'PASSWORD': getenv('MONITORPASS', _rand())
    }

if not secret_key:
    secret_key = _rand()

_jwrite(secret_key_json, secret_key)
_jwrite(auth_json, auth)

USERNAME = auth['USERNAME']
PASSWORD = auth['PASSWORD']

SECRET_KEY = secret_key
WTF_CSRF_ENABLED = True

DATABASE = path.join(datadir, 'redabas.sqlite')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE
SPACEAPI_JSON = path.join(basedir, 'spaceapi.json')

MAXKEEP = 60 * 60 * 24 * 14
MAXCONC = 60 * 60 * 2

AUTOREF_MIN = 15
AUTOREF_MAX = 30

LOGOS = ['evil_man.png', 'plug.png']
SPACE_LOGO = 'cccmz_logo.png'
SPACE_OPEN = 'space_open.png'
SPACE_CLOSED = 'space_closed.png'
SPACE_SENSORS = {
    'network_connections': ['traffic4out'],
    'power_consumption': ['leases'],
    'door_locked': ['traffic4in', 'traffic6out']
}
