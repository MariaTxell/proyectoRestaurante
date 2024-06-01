# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from apps.home.models import db, Restaurante, Reserva
from apps.authentication.models import Users
from apps.home.forms import ReservaForm
from apps.authentication.forms import EditAccountForm
from jinja2 import TemplateNotFound
from apps.authentication.util import hash_pass
from sqlalchemy.orm import joinedload
from datetime import datetime


@blueprint.route('/index')
@login_required
def index():
    restaurantes = Restaurante.query.all()

    # Filtrar los restaurantes que tienen mesas disponibles
    restaurantes_disponibles = []
    for restaurante in restaurantes:
        mesas_disponibles = obtener_mesas_disponibles(restaurante.id_restaurante)
        if mesas_disponibles:
            restaurantes_disponibles.append(restaurante)
    
    # Filtrar los restaurantes que tienen reservas este mes
    reservas_por_restaurante = {}
    for restaurante in restaurantes_disponibles:
        reservas_del_mes = Reserva.query.filter(
            Reserva.id_restaurante == restaurante.id_restaurante,
            Reserva.dia >= datetime.now().replace(day=1).date()  # Primer día de este mes
        ).count()
        reservas_por_restaurante[restaurante.id_restaurante] = reservas_del_mes
    
    # Ordenar los restaurantes por el número de reservas este mes en orden descendente
    restaurantes_ordenados_por_reservas = sorted(restaurantes_disponibles, key=lambda x: reservas_por_restaurante.get(x.id_restaurante, 0), reverse=True)
    
    # Obtener los tres primeros restaurantes con el mayor número de reservas este mes
    tres_primeros = restaurantes_ordenados_por_reservas[:3]
    
    return render_template('home/index.html', restaurantes=tres_primeros)

# Definir una función para obtener las mesas disponibles para un restaurante específico
def obtener_mesas_disponibles(id_restaurante):
    restaurante = Restaurante.query.get(id_restaurante)
    if restaurante:
        reservas = Reserva.query.filter(
            Reserva.id_restaurante == id_restaurante,
            Reserva.dia >= datetime.now().date()
        ).all()

        # Mesas reservadas en el mismo restaurante
        mesas_reservadas = {reserva.mesa for reserva in reservas}

        # Obtener todas las mesas del restaurante
        mesas = list(range(1, restaurante.numero_mesas + 1))

        # Filtrar mesas disponibles
        mesas_disponibles = [(mesa, f"Mesa {mesa}") for mesa in mesas if mesa not in mesas_reservadas]
        #mesas_disponibles = [mesa for mesa in range(1, restaurante.numero_mesas + 1) if mesa not in mesas_reservadas]
        return mesas_disponibles
    return []

@blueprint.route('/buscar_restaurantes', methods=['GET', 'POST'])
@login_required
def buscar_restaurantes():
    if request.method == 'POST':
        # Procesar los filtros del formulario
        nombre = request.form.get('nombre')
        tipo_cocina = request.form.get('tipo_cocina')
        ubicacion = request.form.get('ubicacion')
        horario = request.form.get('horario')
        filtros = []
        if nombre:
            filtros.append(Restaurante.nombre.contains(nombre))
        if tipo_cocina:
            filtros.append(Restaurante.tipo_cocina == tipo_cocina)
        if ubicacion:
            filtros.append(Restaurante.ubicacion == ubicacion)
        if horario:
            filtros.append(Restaurante.horario == horario)
        restaurantes = Restaurante.query.filter(*filtros).all()
    
    else:
        # Obtener todos los restaurantes si no hay filtros
        restaurantes = Restaurante.query.all()
    
    # Filtrar los restaurantes que tienen mesas disponibles
    restaurantes_disponibles = []
    for restaurante in restaurantes:
        mesas_disponibles = obtener_mesas_disponibles(restaurante.id_restaurante)
        if mesas_disponibles:
            restaurantes_disponibles.append(restaurante)

    id_restaurante = request.args.get('id')
    if id_restaurante:
        # Si se pasa un id, cargar el restaurante correspondiente
        restaurante = Restaurante.query.get(id_restaurante)
        if restaurante:
            restaurantes_disponibles = Restaurante.query.filter_by(nombre=restaurante.nombre).all()
            return render_template('home/buscar_restaurantes.html', restaurantes=restaurantes_disponibles, restaurante=restaurante)
    return render_template('home/buscar_restaurantes.html', restaurantes=restaurantes_disponibles)

@blueprint.route('/realizar_reserva/<int:id>', methods=['GET', 'POST'])
@login_required
def realizar_reserva(id):
    restaurante = Restaurante.query.get_or_404(id)
    form = ReservaForm()
    usuario = Users.query.filter_by(username=current_user.username).first()
    
    # Obtener las mesas disponibles llamando a la función
    mesas_disponibles = obtener_mesas_disponibles(id)

    # Actualizar las opciones del SelectField de mesa
    form.mesa.choices = mesas_disponibles
    
    if form.validate_on_submit():
        if form.dia.data < datetime.now().date():
            flash('No puedes hacer una reserva para una fecha pasada', 'danger')
        else:
            reserva = Reserva(
                id_restaurante=restaurante.id_restaurante,
                dia=form.dia.data,
                hora=form.hora.data,
                mesa=form.mesa.data,
                numero_personas=form.numero_personas.data,
                id_usuario=usuario.id_usuario
            )
            db.session.add(reserva)
            db.session.commit()
            flash('Reserva realizada con éxito', 'success')
            return redirect(url_for('home_blueprint.mi_cuenta'))
    return render_template('home/reserva_restaurante.html', restaurante=restaurante, form=form)

@blueprint.route('/cancelar_reserva/<int:id>', methods=['GET', 'POST'])
@login_required
def cancelar_reserva(id):
    reserva = Reserva.query.get(id)
    if reserva:
        if reserva.dia > datetime.now().date():
            # Si la fecha actual es anterior a la fecha de la reserva, entonces se puede cancelar
            db.session.delete(reserva)
            db.session.commit()
            flash('Reserva cancelada correctamente', 'success')
            print("eliminado")
        else:
            # Si la fecha actual es igual o posterior a la fecha de la reserva, no se puede cancelar
            flash('No se puede cancelar una reserva que ya ha pasado', 'danger')
            print("no")
    else:
        flash('Reserva no encontrada', 'danger')
        print("fuera")

    return redirect(url_for('home_blueprint.mi_cuenta'))


@blueprint.route('/mi_cuenta')
@login_required
def mi_cuenta():
    now = datetime.now()
    usuario = Users.query.filter_by(username=current_user.username).first()
    reservas = Reserva.query.filter_by(id_usuario=usuario.id_usuario).options(joinedload(Reserva.restaurante_relacion)).all()
    return render_template('home/mi_cuenta.html', now=now, reservas=reservas)

@blueprint.route('/update_email', methods=['GET', 'POST'])
@login_required
def update_email():
    if request.method == 'POST':
        new_email = request.form.get('email')
        if new_email:
            current_user.email = new_email
            db.session.commit()
            flash('Correo actualizado con éxito', 'success')
            return redirect(url_for('home_blueprint.mi_cuenta'))
    return render_template('home/update_email.html')

@blueprint.route('/update_password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Contraseña actual incorrecta', 'danger')
        return redirect(url_for('home_blueprint.update_password'))
    
    if new_password != confirm_password:
        flash('Las nuevas contraseñas no coinciden', 'danger')
        return redirect(url_for('home_blueprint.update_password'))
    
    current_user.password = hash_pass(new_password)
    db.session.commit()
    flash('Contraseña actualizada con éxito', 'success')
    return render_template('home/update_password.html')

@blueprint.route('/contacto')
@login_required
def contacto():
    usuario = Users.query.filter_by(username=current_user.username).first()
    return render_template('home/contacto.html', usuario=usuario)

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
    
    
