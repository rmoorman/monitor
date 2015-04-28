from flask.ext.restful import Resource, abort
from flask.ext.restful.reqparse import RequestParser

from application import api, db
from application.auth import requires_auth
from application.models import Collection, Data, Sensor, Unit
from application.service import (
    handle_variation,
    retrieve_dbo,
    sanitize_name,
    short_conclusions,
    the_axis,
    the_non_collection
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


class AxisHandler(Resource):
    def get(self):
        return the_axis


class ConcHandler(Resource):
    def get(self, cc=0.0):
        conclusions = short_conclusions()
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
        if name:
            return retrieve_dbo(Collection, name).api_repr()
        return [c.name for c in Collection.query.all()]

    @requires_auth
    def post(self, name=None):
        a = _get_input(['name', 'sensors'])
        collection = retrieve_dbo(Collection, a.get('name'), create=True)
        description = a.get('description')
        if description:
            collection.description = description
        for s in a.get('sensors', []):
            sensor = retrieve_dbo(Sensor, s)
            sensor.collection = collection
            db.session.add(sensor)
        db.session.commit()

        return a


class SensorHandler(Resource):
    def get(self, name=None):
        if name:
            return retrieve_dbo(Sensor, name).api_repr()
        return [s.name for s in Sensor.query.all()]

    @requires_auth
    def post(self, name=None):
        a = _get_input(['name', 'unit'])
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
            sensor = retrieve_dbo(Sensor, sensorname)
            return [data.api_repr() for data in sensor.get_data().all()]
        abort(400, error='please specify a sensor')

    @requires_auth
    def post(self, sensorname=None):
        a = _get_input(['value', 'sensor'])
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
        if not any([d for d in data if str(d.ms()) == a.get('time')]):
            abort(400, error='given time does not match', time=a.get('time'))
        for dt in [d for d in data if str(d.ms()) == a.get('time')]:
            db.session.delete(dt)
        db.session.commit()

        return a


class GraphHandler(Resource):
    def get(self, collectionname=None):
        non_collection = None
        if collectionname:
            collection = non_collection if collectionname == the_non_collection else retrieve_dbo(Collection, collectionname)
            return [
                sensor.flot_repr() for sensor in Sensor.query.filter(Sensor.collection == collection).order_by(Sensor.name.asc()).all()
                if sensor and sensor.unit and sensor.unit.axis in the_axis.keys()
            ]
        res = [c.name for c in Collection.query.order_by(Collection.name.asc()).all() if c.sensors.count() and any([s.unit.axis for s in c.sensors.all()])]
        return res + [the_non_collection] if Sensor.query.filter(Sensor.collection == non_collection).count() else res


api.add_resource(AxisHandler, '/axis', '/axis/')
api.add_resource(CollectionHandler, '/collection', '/collection/', '/collection/<string:name>')
api.add_resource(ConcHandler, '/%', '/%/', '/<int:cc>%', '/<float:cc>%')
api.add_resource(DataHandler, '/data', '/data/', '/data/<string:sensorname>')
api.add_resource(GraphHandler, '/graph', '/graph/', '/graph/<string:collectionname>')
api.add_resource(SensorHandler, '/sensor', '/sensor/', '/sensor/<string:name>')
api.add_resource(SpaceHandler, '/space', '/space/', '/SpaceAPI', '/SpaceAPI/')
api.add_resource(UnitHandler, '/unit', '/unit/', '/unit/<string:name>')
