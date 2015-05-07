from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declared_attr

from application import app, db


def cliff():
    return datetime.utcnow() - timedelta(seconds=app.config['MAXCONC'])


def del_cliff():
    return datetime.utcnow() - timedelta(seconds=app.config['MAXKEEP'])


class BaseModel(object):
    id = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(cls):
        return '<{} #{}{}>'.format(cls.__tablename__, cls.id, ' "{}"'.format(cls.name) if hasattr(cls, 'name') else '')

    def __iter__(cls):
        values = vars(cls)
        for attr in cls.__table__.columns.keys():
            if attr in values and not attr.endswith('id'):
                yield attr, values[attr]

    def show(cls):
        return dict(cls)


class Unit(BaseModel, db.Model):
    name = db.Column(db.String, unique=True)
    axis = db.Column(db.Integer)
    description = db.Column(db.Text)

    def __init__(self, name, axis=1):
        self.name = name
        self.axis = axis

    def api_repr(self):
        res = self.show()
        res.update(sensors=[s.name for s in self.sensors])
        return res


class Collection(BaseModel, db.Model):
    name = db.Column(db.String, unique=True)
    description = db.Column(db.Text)

    def __init__(self, name):
        self.name = name

    def api_repr(self):
        res = self.show()
        res.update(sensors=[s.name for s in self.sensors])
        return res


class Sensor(BaseModel, db.Model):
    name = db.Column(db.String, unique=True)
    factor = db.Column(db.Float)
    description = db.Column(db.Text)

    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unit = db.relationship('Unit', backref=db.backref('sensors', lazy='dynamic', cascade='all,delete'), post_update=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    collection = db.relationship('Collection', backref=db.backref('sensors', lazy='dynamic', cascade='all,delete'), post_update=True)

    def __init__(self, name, unit, factor=0.0):
        self.name = name
        self.unit = unit
        self.factor = factor

    def get_data(self, capped=False):
        data = self.data.order_by(Data.time.desc())
        return data.filter(Data.time > cliff()) if capped else data

    def api_repr(self, as_num=True):
        res = self.show()
        if self.collection:
            res.update(collection=self.collection.name)
        if self.unit:
            res.update(unit=self.unit.name)
            res.update(unit_axis=self.unit.axis)
        res.update(data_len=self.data.count())
        latest = self.get_data().first()
        if latest:
            res.update(data_latest=latest.api_repr(as_num))
            res.update(data_fresh=(latest.time > cliff()))
        return res

    def flot_repr(self):
        return dict(
            label=self.name,
            yaxis=self.unit.axis,
            data=[d.flot_repr() for d in self.get_data().all()]
        )


class Data(BaseModel, db.Model):
    time = db.Column(db.DateTime)
    value = db.Column(db.String)

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    sensor = db.relationship('Sensor', backref=db.backref('data', lazy='dynamic', order_by=time.desc(), cascade='all,delete'), post_update=True)

    def __init__(self, value, sensor):
        for old in self.query.filter(Data.time < del_cliff()).all():
            db.session.delete(old)

        self.time = datetime.utcnow()
        self.value = value
        self.sensor = sensor

    def ms(self):
        if self.time:
            return int(1000 * (self.time - datetime.utcfromtimestamp(0)).total_seconds())

    def num(self):
        try:
            return float(self.value)
        except ValueError:
            pass

    def api_repr(self, as_num=True):
        return dict(time=self.ms(), value=self.num() if as_num else self.value)

    def flot_repr(self):
        return [self.ms(), self.num()]
