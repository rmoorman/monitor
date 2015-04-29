from flask import url_for

from application import app
from application.models import Data, Sensor
from application.service import short_conclusions, the_shouts
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
        val = sensor.get_data().first().num(fallback=False)
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

    shouts = Sensor.query.filter(Sensor.name == the_shouts).first()
    lshout = shouts.get_data().first().num(fallback=True) if shouts and shouts.get_data().first() else None

    _set_field(['state', 'message'], '{}% chance someone is there! last message: \'{}\''.format(conclusions, lshout if lshout else 'none'))

    _set_field(['icon', 'closed'], closed_url)
    _set_field(['icon', 'open'], open_url)
    _set_field(['logo'], logo_url)
    _set_field(['open'], space_is_open)
    _set_field(['state', 'icon', 'closed'], closed_url)
    _set_field(['state', 'icon', 'open'], open_url)
    _set_field(['state', 'open'], space_is_open)

    return _space_skel
