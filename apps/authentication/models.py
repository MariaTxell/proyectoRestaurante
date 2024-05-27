# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):

    __tablename__ = 'lista_usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    #password = db.Column(db.LargeBinary)
    password = db.Column(db.String(128))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)
                print(f'Password hashed: {value}')  # Agregar esta línea para depuración

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)
    
    def get_id(self):
        """Devuelve el id del usuario"""
        return self.id_usuario


@login_manager.user_loader
def user_loader(id_usuario):
    return Users.query.filter_by(id_usuario=id_usuario).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
