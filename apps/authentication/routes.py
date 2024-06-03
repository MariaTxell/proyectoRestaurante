# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm, UpdateEmailForm, UpdatePasswordForm
from apps.authentication.models import Users
from apps.authentication.util import verify_pass, hash_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Verificar conexión a la base de datos
        try:
            db.session.execute('SELECT 1')
            print("Conexión a la base de datos exitosa.")
        except Exception as e:
            print(f"Error en la conexión a la base de datos: {e}")
            return render_template('accounts/login.html', msg='Database connection error', form=login_form)

        # Locate user
        #user = Users.query.filter_by(username=username).first()
        try:
            user = Users.query.filter_by(username=username).first()
            print(f"Usuario encontrado: {user}")
        except Exception as e:
            print(f"Error al buscar el usuario: {e}")
            return render_template('accounts/login.html', msg='Error interno', form=login_form)
        
        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('home_blueprint.index'))
            #return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html', form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='El nombre de usuario ya está registrado',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='El correo electrónico ya está registrado',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='Usuario creado con éxito.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)
    
# Ruta para actualizar el correo electrónico del usuario
@blueprint.route('/update_email', methods=['GET', 'POST'])
def update_email():
    form = UpdateEmailForm(request.form)

    # Comprobar si el formulario ha sido enviado y es válido
    if form.validate_on_submit():
        # Acceder al dato del campo de correo electrónico
        email = form.email.data
                
        # Buscar el usuario actual en la base de datos utilizando el username
        usuario = Users.query.filter_by(username=current_user.username).first()
        
        # Comprobar si el nuevo correo electrónico ya existe para otro usuario
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            return render_template('home/update_email.html',
                                   msg='El correo electrónico ya está en uso por otro usuario',
                                   success=False,
                                   form=form)
        else:
            usuario.email = email
            try:
                db.session.commit()  # Confirmar los cambios en la base de datos
                print("Correo actualizado con éxito")
            except Exception as e:
                db.session.rollback()  # Revertir la transacción en caso de error
                return render_template('home/update_email.html',
                                   msg='Error al actualizar el correo electrónico:  + {{ str(e) }}',
                                   success=False,
                                   form=form)

            # Redirigir al usuario a su cuenta después de la actualización
            return redirect(url_for('home_blueprint.mi_cuenta'))
    
    # Renderizar la plantilla con el formulario
    return render_template('home/update_email.html', form=form)

# Ruta para actualizar la contraseña del usuario
@blueprint.route('/update_password', methods=['GET', 'POST'])
def update_password():
    form = UpdatePasswordForm()

    # Comprobar si el formulario ha sido enviado y es válido
    if form.validate_on_submit():
        # Buscar el usuario actual en la base de datos utilizando el username
        usuario = Users.query.filter_by(username=current_user.username).first()

        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        
        if new_password != confirm_password:
            return render_template('home/update_password.html',
                                   msg='Las nuevas contraseñas no coinciden',
                                   success=False,
                                   form=form)
        
        usuario.password = hash_pass(new_password)
        db.session.commit()
        print('Contraseña actualizada con éxito', 'success')
        return redirect(url_for('home_blueprint.mi_cuenta'))
    return render_template('home/update_password.html', form=form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
