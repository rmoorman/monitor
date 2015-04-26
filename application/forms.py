from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class ShoutForm(Form):
    shout = StringField('nachricht', validators=[InputRequired('Inhalt fehlt!'), Length(min=5, max=142, message='Mindestens %(min)d, maximal %(max)d Zeichen')])
    save = SubmitField('los')
