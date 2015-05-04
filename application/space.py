from random import choice
from flask import url_for

from application import app
from application.conc import short_conclusions
from application.models import Data, Sensor
from application.service import get_shouts
from config import _jread

_space_skel = _jread(app.config['SPACEAPI_JSON'])


def spaceapi():
    def _set_field(field_path, value):
        if _space_skel:
            scope = _space_skel
            for field in field_path:
                if field in scope.keys():
                    if field == field_path[-1]:
                        scope[field] = value
                    scope = scope[field]

    def _sensor_elem(apisens, sensor):
        last = sensor.get_data().first()
        if last:
            val = last.num(fallback=False)
            res = {
                'description': sensor.description,
                'location': sensor.description,
                'name': sensor.name,
                'value': val
            }
            if apisens == 'power_consumption':
                res.update({'unit': 'W'})
            if apisens == 'door_locked':
                res.update({'value': not val})
            return res

    conclusions = short_conclusions()
    shouts = get_shouts()

    space_is_open = True if conclusions >= 100 else False
    logo_url = url_for('static', filename=app.config['SPACE_LOGO'], _external=True)
    open_url = url_for('static', filename=app.config['SPACE_OPEN'], _external=True)
    closed_url = url_for('static', filename=app.config['SPACE_CLOSED'], _external=True)

    for apisens, sensors in app.config['SPACE_SENSORS'].items():
        _set_field(['sensors', apisens], [
            _sensor_elem(apisens, sensor) for sensor in [
                Sensor.query.filter(Sensor.name == s).first() for s in sensors
            ] if sensor is not None and sensor.get_data().first()
        ])

    latest_data = Data.query.order_by(Data.time.desc()).first()
    if latest_data:
        _set_field(['state', 'lastchange'], latest_data.ms())

    last_shout = shouts.get_data().first()
    _set_field(['state', 'message'], '{}% chance someone is there! last message: \'{}\''.format(
        conclusions,
        last_shout.value if last_shout else 'no shouts, sorry')
    )

    _set_field(['contact', 'twitter'], choice(['@cccmz', '@cccmzwi']))
    _set_field(['icon', 'closed'], closed_url)
    _set_field(['icon', 'open'], open_url)
    _set_field(['logo'], logo_url)
    _set_field(['open'], space_is_open)
    _set_field(['state', 'icon', 'closed'], closed_url)
    _set_field(['state', 'icon', 'open'], open_url)
    _set_field(['state', 'open'], space_is_open)

    return _space_skel
