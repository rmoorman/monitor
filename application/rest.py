from flask.ext.restful import Resource, abort
from flask.ext.restful.reqparse import RequestParser

from application import api, db
from application.auth import requires_auth
from application.conc import jump_to_conclusions
from application.models import Collection, Data, Sensor, Unit
from application.service import (
    get_shouts,
    get_variation,
    handle_variation,
    retrieve_dbo,
    sanitize_name,
    the_axis,
    the_non_collection,
    the_shouts,
    the_variation
)
from application.space import spaceapi

parser = RequestParser()
parser.add_argument('axis', type=int)
parser.add_argument('description', type=str)
parser.add_argument('factor', type=float)
parser.add_argument('name', type=str)
parser.add_argument('sensor', type=str)
parser.add_argument('sensors', type=str, action='append')
parser.add_argument('time', type=str)
parser.add_argument('unit', type=str)
parser.add_argument('value', type=str)


def _get_input(req, opt=None):
    args = parser.parse_args()
    args.name = sanitize_name(args.name)
    args.sensor = sanitize_name(args.sensor)
    args.sensors = [sanitize_name(sensor) for sensor in args.sensors] if args.sensors else None
    args.unit = sanitize_name(args.unit)

    if args.axis and args.axis not in the_axis.keys():
        abort(400, error='given axis is not permitted')

    cargs = dict((a, args[a]) for a in args if args[a] is not None)

    if not all([cargs.get(r) for r in req]):
        abort(400, error='please specify all required arguments', expected=req)
    if opt and not any([cargs.get(o) for o in opt]):
        abort(400, error='please specify at least one (optional) argument', expected=opt)

    return cargs


def _ensure_service_env(name):
        get_shouts() if name == the_shouts else None
        get_variation() if name == the_variation else None


class AxisHandler(Resource):
    def get(self):
        return the_axis


class ConcHandler(Resource):
    def get(self, cc=0.0):
        conclusions = jump_to_conclusions()
        if cc and cc != conclusions:
            handle_variation(cc, conclusions)
        return conclusions


class SpaceHandler(Resource):
    def get(self):
        return spaceapi()


class UnitHandler(Resource):
    def get(self, name=None):
        if name:
            return retrieve_dbo(Unit, name).api_repr()
        return [u.name for u in Unit.query.all()]

    @requires_auth
    def post(self, name=None):
        a = _get_input(['name'], opt=['axis', 'description'])
        unit = retrieve_dbo(Unit, a.get('name'), create=True)
        axis, description = a.get('axis'), a.get('description')
        if axis is not None:
            unit.axis = axis
        if description:
            unit.description = description
        db.session.add(unit)
        db.session.commit()

        return a


class CollectionHandler(Resource):
    def get(self, name=None):
        non_collection = None
        non_sensors = Sensor.query.filter(Sensor.collection == non_collection)
        if name:
            if name != the_non_collection:
                return retrieve_dbo(Collection, name).api_repr()
            return {
                'description': 'The Non-Collection',
                'name': the_non_collection,
                'sensors': [s.name for s in non_sensors.all()]
            }

        res = [c.name for c in Collection.query.all()]
        return sorted(res + [the_non_collection] if non_sensors.count() else res)

    @requires_auth
    def post(self, name=None):
        a = _get_input(['name', 'sensors'])
        collection = None
        if a.get('name') != the_non_collection:
            collection = retrieve_dbo(Collection, a.get('name'), create=True)
            description = a.get('description')
            if description:
                collection.description = description

        for s in a.get('sensors', []):
            sensor = retrieve_dbo(Sensor, s)
            if a.get('name') == the_non_collection:
                sensor.collection_id = None
            sensor.collection = collection
            db.session.add(sensor)
        db.session.commit()

        return a


class SensorHandler(Resource):
    def get(self, name=None):
        if name:
            _ensure_service_env(name)
            return retrieve_dbo(Sensor, name).api_repr(as_num=True if name != the_shouts else False)
        return [s.name for s in Sensor.query.all()]

    @requires_auth
    def post(self, name=None):
        a = _get_input(['name', 'unit'])
        _ensure_service_env(a.get('name'))
        unit = retrieve_dbo(Unit, a.get('unit'))
        sensor = retrieve_dbo(Sensor, a.get('name'), create=unit)
        sensor.unit = unit
        description, factor = a.get('description'), a.get('factor')
        if description:
            sensor.description = description
        if factor is not None:
            sensor.factor = factor
        db.session.add(sensor)
        db.session.commit()

        return a


class DataHandler(Resource):
    def get(self, sensorname=None):
        if sensorname:
            _ensure_service_env(sensorname)
            return [data.api_repr(as_num=True if sensorname != the_shouts else False) for data in retrieve_dbo(Sensor, sensorname).get_data().all()]
        abort(400, error='please specify a sensor')

    @requires_auth
    def post(self, sensorname=None):
        a = _get_input(['value', 'sensor'])
        _ensure_service_env(a.get('sensor'))
        data = Data(a.get('value'), retrieve_dbo(Sensor, a.get('sensor')))
        db.session.add(data)
        db.session.commit()

        return a

    @requires_auth
    def delete(self, sensorname=None):
        a = _get_input(['value', 'time'])
        data = Data.query.filter(Data.value == a.get('value')).all()
        if not data:
            abort(400, error='given value is unknown', value=a.get('value'))
        # there can be multiple data with the same value
        if not any([
            (d, db.session.delete(d))[0] for d in data if str(d.ms()) == a.get('time')
        ]):
            abort(400, error='given time does not match', time=a.get('time'))
        db.session.commit()

        return a


class GraphHandler(Resource):
    def get(self, collectionname=None):
        def _chk_sens(s):
            return all([
                s.unit,
                s.unit.axis in the_axis.keys(),
                s.get_data().first()
            ])
        non_collection = None
        if collectionname:
            collection = non_collection if collectionname == the_non_collection else retrieve_dbo(Collection, collectionname)
            return [
                sensor.flot_repr() for sensor in Sensor.query.filter(Sensor.collection == collection).order_by(Sensor.name.asc()).all()
                if _chk_sens(sensor)
            ]
        return sorted(set([
            sensor.collection.name if sensor.collection != non_collection else the_non_collection for sensor in Sensor.query.all()
            if _chk_sens(sensor)
        ]))

api.add_resource(AxisHandler, '/axis', '/axis/')
api.add_resource(CollectionHandler, '/collection', '/collection/', '/collection/<string:name>')
api.add_resource(ConcHandler, '/%', '/%/', '/<int:cc>', '/<float:cc>', '/<int:cc>/', '/<float:cc>/')
api.add_resource(DataHandler, '/data', '/data/', '/data/<string:sensorname>')
api.add_resource(GraphHandler, '/graph', '/graph/', '/graph/<string:collectionname>')
api.add_resource(SensorHandler, '/sensor', '/sensor/', '/sensor/<string:name>')
api.add_resource(SpaceHandler, '/space', '/space/')
api.add_resource(UnitHandler, '/unit', '/unit/', '/unit/<string:name>')
