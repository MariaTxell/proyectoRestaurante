# apps/reservas/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Restaurante(db.Model):
    __tablename__ = 'lista_restaurantes'
    id_restaurante = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_cocina = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    numero_mesas = db.Column(db.Integer, nullable=False)
    horario = db.Column(db.String(100), nullable=False)
    reserv_restaurante = db.relationship('Reserva', backref='restaurante', overlaps='reservas_restaurante')

class Reserva(db.Model):
    __tablename__ = 'restaurante_reserva'
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_restaurante = db.Column(db.Integer, db.ForeignKey('lista_restaurantes.id_restaurante'), nullable=False)
    dia = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    mesa = db.Column(db.String(10), nullable=False)
    numero_personas = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    # Define the relationship to Restaurante
    restaurante_relacion = db.relationship('Restaurante', backref='reservas', overlaps='reservas_restaurante')
