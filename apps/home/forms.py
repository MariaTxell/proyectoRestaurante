# apps/reservas/forms.py
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired

class ReservaForm(FlaskForm):
    dia = DateField('Dia', format='%Y-%m-%d', validators=[DataRequired()])
    hora = TimeField('Hora', format='%H:%M', validators=[DataRequired()])
    mesa = SelectField('Mesa', choices=[], coerce=int, validators=[DataRequired()])
    numero_personas = IntegerField('Número de Personas', validators=[DataRequired()])
    submit = SubmitField('Reservar')