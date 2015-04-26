from datetime import datetime, timedelta
from string import ascii_letters, digits

from flask import flash
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
        res = ''.join([c for c in mstr if c in (ascii_letters + digits + '-._')]).lower()
        print('mstr:', mstr, 'res:', res)
        return res


def retrieve_dbo(mdl, name, create=False):
    name = sanitize_name(name)
    dbo = mdl.query.filter(mdl.name == name).first()
    if not dbo:
        if not create:
            abort(400, error='given name is unknown', name=name)
        dbo = mdl(name) if create is True else mdl(name, create) if create else mdl(name)
        db.session.add(dbo)
    return dbo


def _cliff():
    return (datetime.utcnow() - timedelta(seconds=app.config['MAXCONC']))


def the_cliff():
    return int(1000 * (datetime.utcnow() - datetime.utcfromtimestamp(app.config['MAXCONC'])).total_seconds())


def the_del_cliff():
    return int(1000 * (datetime.utcnow() - datetime.utcfromtimestamp(app.config['MAXKEEP'])).total_seconds())


def _ccnv(stf, fac):
    res = None
    if stf and fac:
        try:
            res = round(float(stf) * fac, 2)
        except ValueError:
            pass
    return res


def short_conclusions():
    result = 0.0

    for sensor in Sensor.query.filter(Sensor.factor > 0.0).all():
        last = sensor.get_data().filter(Data.time > _cliff()).first()
        if last and last.value:
            res = _ccnv(last.value, sensor.factor)
            if res:
                result += res
    return round(result, 2)


def jump_to_conclusions_mat():
    result = list()
    rsum = 0.0
    for collection in Collection.query.order_by(Collection.name.asc()).all() + [None]:
        cresult = list()
        csum = 0.0
        for sensor in Sensor.query.filter(Sensor.collection == collection).order_by(Sensor.name.asc()).all():
            ssum = None
            last = sensor.get_data().filter(Data.time > _cliff()).first()
            if last and last.value:
                ssum = _ccnv(last.value, sensor.factor)
                if ssum:
                    csum += ssum
                    rsum += ssum
            cresult.append((ssum, sensor))
        if len(cresult):
            result.append((round(csum, 2), collection, cresult))
    return (round(rsum, 2), result)


def _service_collection(sensor):
    collection = retrieve_dbo(Collection, the_service_collection, create=True)
    collection.description = 'System-Sammlung'
    db.session.add(collection)

    if sensor:
        sensor.collection = collection
        db.session.add(sensor)


def handle_shout(form):
    if form.validate():
        data = form.data

        unit = retrieve_dbo(Unit, the_shouts, create=True)
        unit.description = 'Nachrichten-Einheit'
        unit.axis = 0
        db.session.add(unit)

        sensor = retrieve_dbo(Sensor, the_shouts, create=unit)
        sensor.description = 'Nachrichten-Sensor'
        sensor.factor = 0.0
        db.session.add(sensor)

        _service_collection(sensor)

        if data.get('save'):
            if not Data.query.filter(Data.value == data.get('shout')).count():
                shout = Data(data.get('shout'), sensor)
                db.session.add(shout)
                flash('ok')
            else:
                flash('hatten wir schon')

        db.session.commit()


def handle_variation(given, expected):
    unit = retrieve_dbo(Unit, the_variation_unit, create=True)
    unit.description = 'Erdstrahlenbelastung in Bovis'
    unit.axis = 1
    db.session.add(unit)

    sensor = retrieve_dbo(Sensor, the_variation, create=unit)
    sensor.description = 'Erdstrahlenberechnung im Hartmann-Gitter'
    sensor.factor = 0.0
    db.session.add(sensor)

    _service_collection(sensor)

    vr = round(abs(given - expected), 2)
    variation = Data(vr, sensor)
    db.session.add(variation)
    flash('{}: {}'.format(the_variation, vr))
    db.session.commit()


app.jinja_env.globals.update(the_autoref_max=1000*app.config['AUTOREF_MAX'])
app.jinja_env.globals.update(the_autoref_min=1000*app.config['AUTOREF_MIN'])
app.jinja_env.globals.update(the_axis=the_axis)
app.jinja_env.globals.update(the_cliff=the_cliff)
app.jinja_env.globals.update(the_del_cliff=the_del_cliff)
app.jinja_env.globals.update(the_non_collection=the_non_collection)
app.jinja_env.globals.update(the_service_collection=the_service_collection)
app.jinja_env.globals.update(the_shouts=the_shouts)
app.jinja_env.globals.update(the_variation=the_variation)
app.jinja_env.globals.update(the_variation_unit=the_variation_unit)
