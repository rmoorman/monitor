from datetime import datetime
from string import ascii_letters, digits

from flask.ext.restful import abort

from application import app, db
from application.models import Collection, Data, Sensor, Unit

the_axis = {
    1: 'plain numbers',
    2: 'bytes',
    3: 'epoch seconds'
}
the_non_collection = 'etc'
the_service_collection = 'service'
the_shouts = 'shouts'
the_variation = 'erdstrahlen'
the_variation_unit = 'bovis'

app.jinja_env.line_statement_prefix = '%'
app.jinja_env.line_comment_prefix = '###'


def sanitize_name(mstr):
    if mstr:
        return ''.join([c for c in mstr if c in (ascii_letters + digits + '-._')]).lower()


def retrieve_dbo(mdl, name, create=False):
    name = sanitize_name(name)
    dbo = mdl.query.filter(mdl.name == name).first()
    if not dbo:
        if not create:
            abort(400, error='given name is unknown', name=name)
        dbo = mdl(name) if create is True else mdl(name, create) if create else mdl(name)
        db.session.add(dbo)
    return dbo


def the_cliff():
    return int(1000 * (datetime.utcnow() - datetime.utcfromtimestamp(app.config['MAXCONC'])).total_seconds())


def the_del_cliff():
    return int(1000 * (datetime.utcnow() - datetime.utcfromtimestamp(app.config['MAXKEEP'])).total_seconds())


def _service_sensor(unit_name, sensor_name, axis=0, factor=0.0, sensor_description=None, unit_description=None):
    unit = retrieve_dbo(Unit, unit_name, create=True)
    unit.description = unit_description
    unit.axis = axis
    db.session.add(unit)

    collection = retrieve_dbo(Collection, the_service_collection, create=True)
    collection.description = 'System-Sammlung'
    db.session.add(collection)

    sensor = retrieve_dbo(Sensor, sensor_name, create=unit)
    sensor.description = sensor_description
    sensor.factor = factor
    sensor.collection = collection
    db.session.add(sensor)

    db.session.commit()
    return sensor


def get_shouts():
    return _service_sensor(
        the_shouts,
        the_shouts,
        axis=0,
        factor=0.0,
        sensor_description='Nachrichten-Sensor',
        unit_description='Nachrichten-Einheit',
    )


def get_variation():
    return _service_sensor(
        the_variation_unit,
        the_variation,
        axis=1,
        factor=0.0,
        sensor_description='Erdstrahlenerfassung im Hartmann-Gitter',
        unit_description='Erdstrahlenbelastung in Bovis',
    )


def handle_variation(given, expected):
    sensor = get_variation()
    variation = Data(
        round(abs(given - expected), 2),
        sensor
    )
    db.session.add(variation)
    db.session.commit()


app.jinja_env.globals.update(the_autoref_max=1000*app.config['AUTOREF_MAX'])
app.jinja_env.globals.update(the_autoref_min=1000*app.config['AUTOREF_MIN'])
app.jinja_env.globals.update(the_footer_links=app.config['FOOTER_LINKS'])
app.jinja_env.globals.update(the_axis=the_axis)
app.jinja_env.globals.update(the_cliff=the_cliff)
app.jinja_env.globals.update(the_del_cliff=the_del_cliff)
app.jinja_env.globals.update(the_non_collection=the_non_collection)
app.jinja_env.globals.update(the_service_collection=the_service_collection)
app.jinja_env.globals.update(the_shouts=the_shouts)
app.jinja_env.globals.update(the_space_sensors=app.config['SPACE_SENSORS'])
app.jinja_env.globals.update(the_variation=the_variation)
app.jinja_env.globals.update(the_variation_unit=the_variation_unit)
