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
from apps.home.forms import ReservaForm
from jinja2 import TemplateNotFound


@blueprint.route('/index')
@login_required
def index():
    restaurantes = Restaurante.query.limit(3).all()
    print("restaurantes:", restaurantes)
    return render_template('home/index.html', restaurantes=restaurantes)

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
    
    id_restaurante = request.args.get('id')
    if id_restaurante:
        # Si se pasa un id, cargar el restaurante correspondiente
        restaurante = Restaurante.query.get(id_restaurante)
        if restaurante:
            restaurantes = Restaurante.query.filter_by(nombre=restaurante.nombre).all()
            return render_template('home/buscar_restaurantes.html', restaurantes=restaurantes, restaurante=restaurante)
    return render_template('home/buscar_restaurantes.html', restaurantes=restaurantes)

@blueprint.route('/realizar_reserva/<int:id>', methods=['GET', 'POST'])
@login_required
def realizar_reserva(id):
    restaurante = Restaurante.query.get_or_404(id)
    form = ReservaForm()
    if form.validate_on_submit():
        reserva = Reserva(
            id_restaurante=restaurante.id_restaurante,
            dia=form.dia.data,
            hora=form.hora.data,
            mesa=form.mesa.data,
            numero_personas=form.numero_personas.data,
            id_usuario=current_user.id 
        )
        db.session.add(reserva)
        db.session.commit()
        flash('Reserva realizada con éxito', 'success')
        return redirect(url_for('home.mi_cuenta'))
    return render_template('home/reserva_restaurante.html', restaurante=restaurante, form=form)

@blueprint.route('/mi_cuenta')
@login_required
def mi_cuenta():
    reservas = Reserva.query.filter_by(username=current_user.username).all()
    return render_template('home/mi_cuenta.html', reservas=reservas)

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
    
    
