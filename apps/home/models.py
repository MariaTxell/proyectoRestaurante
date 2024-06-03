# apps/reservas/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define el modelo para la tabla de restaurantes
class Restaurante(db.Model):
    __tablename__ = 'lista_restaurantes'
    id_restaurante = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_cocina = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    numero_mesas = db.Column(db.Integer, nullable=False)
    horario = db.Column(db.String(100), nullable=False)
    # Define la relación con las reservas de este restaurante
    reserv_restaurante = db.relationship('Reserva', backref='restaurante', overlaps='reservas_restaurante')

# Define el modelo para la tabla de reservas
class Reserva(db.Model):
    __tablename__ = 'restaurante_reserva'
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_restaurante = db.Column(db.Integer, db.ForeignKey('lista_restaurantes.id_restaurante'), nullable=False)
    dia = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    mesa = db.Column(db.String(10), nullable=False)
    numero_personas = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    # Define la relación con el restaurante al que pertenece esta reserva
    restaurante_relacion = db.relationship('Restaurante', backref='reservas', overlaps='reservas_restaurante')
