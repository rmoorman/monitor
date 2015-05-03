from flask import flash
from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired, Length

from application import db
from application.models import Data
from application.service import get_shouts


class ShoutForm(Form):
    shout = StringField('nachricht', validators=[InputRequired('Inhalt fehlt!'), Length(min=5, max=142, message='Mindestens %(min)d, maximal %(max)d Zeichen')])
    save = SubmitField('los')


def handle_shout(form):
    if form.validate():
        data = form.data
        sensor = get_shouts()

        if data.get('save'):
            if Data.query.filter(Data.value == data.get('shout')).count():
                flash('hatten wir schon')
            else:
                shout = Data(data.get('shout'), sensor)
                db.session.add(shout)
                db.session.commit()
                flash('ok')
