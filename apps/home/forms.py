# apps/reservas/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired

class ReservaForm(FlaskForm):
    dia = StringField('Día', validators=[DataRequired()])
    hora = StringField('Hora', validators=[DataRequired()])
    mesa = StringField('Mesa', validators=[DataRequired()])
    numero_personas = IntegerField('Número de Personas', validators=[DataRequired()])
    submit = SubmitField('Reservar')