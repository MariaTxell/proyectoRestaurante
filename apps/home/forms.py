# apps/reservas/forms.py
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired

# Define los campos del formulario para hacer una reserva
class ReservaForm(FlaskForm):
    dia = DateField('Dia', format='%Y-%m-%d', validators=[DataRequired()])
    hora = SelectField('Hora', choices=[], validators=[DataRequired()]) # Campo para seleccionar la hora, con un select options, se inicializa vacío y se cargará dinámicamente
    mesa = SelectField('Mesa', choices=[], coerce=int, validators=[DataRequired()]) # Campo para seleccionar la mesa, con un select options, se inicializa vacío y se cargará dinámicamente
    numero_personas = IntegerField('Número de Personas', validators=[DataRequired()])
    submit = SubmitField('Reservar')
