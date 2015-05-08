from application.models import Sensor


def _conv_and_calc(value, factor):
    res = None
    if value and factor:
        try:
            res = round(float(value) * factor, 2)
        except ValueError:
            pass
    return res


def jump_to_conclusions():
    result = 0.0
    for sensor in Sensor.query.filter(Sensor.factor > 0.0).all():
        last = sensor.get_data(capped=True).first()
        if last and last.value:
            res = _conv_and_calc(last.value, sensor.factor)
            if res:
                result += res
    return round(result, 2)
