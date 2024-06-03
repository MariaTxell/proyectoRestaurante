# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    

# Definición del formulario para actualizar el correo electrónico
class UpdateEmailForm(FlaskForm):
    email = StringField('Nuevo Email', 
                        id='new_email',
                        validators=[DataRequired(), Email()])


# Definición del formulario para actualizar la contraseña
class UpdatePasswordForm(FlaskForm):
    new_password = PasswordField('Nueva Contraseña', 
                                id='new_password',
                                validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', 
                                    id='confirm_password',
                                    validators=[DataRequired()])