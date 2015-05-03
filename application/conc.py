from application.models import Collection, Data, Sensor
from application.service import cliff


def _conv_and_calc(value, factor):
    res = None
    if value and factor:
        try:
            res = round(float(value) * factor, 2)
        except ValueError:
            pass
    return res


def short_conclusions():
    '''
    be faster because of less input
    '''
    result = 0.0
    for sensor in Sensor.query.filter(Sensor.factor > 0.0).all():
        last = sensor.get_data().filter(Data.time > cliff()).first()
        if last and last.value:
            res = _conv_and_calc(last.value, sensor.factor)
            if res:
                result += res
    return round(result, 2)


def jump_to_conclusions_mat():
    '''
    returns (overall%%, [(collection%%, <collection>, [(sensor%%, <sensor>), ...]), ...])
    '''
    result = list()
    rsum = 0.0
    for collection in Collection.query.order_by(Collection.name.asc()).all() + [None]:
        cresult = list()
        csum = 0.0
        for sensor in Sensor.query.filter(Sensor.collection == collection).order_by(Sensor.name.asc()).all():
            ssum = None
            last = sensor.get_data().filter(Data.time > cliff()).first()
            if last and last.value is not None:
                ssum = _conv_and_calc(last.value, sensor.factor)
                if ssum:
                    csum += ssum
                    rsum += ssum
            cresult.append((ssum, sensor))
        if len(cresult):
            result.append((round(csum, 2), collection, cresult))
    return (round(rsum, 2), result)
