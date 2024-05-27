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
#@login_required
def index():
    restaurantes = Restaurante.query.limit(5).all()
    return render_template('home/index.html', restaurantes=restaurantes)

@blueprint.route('/buscar_restaurantes', methods=['GET', 'POST'])
def buscar_restaurantes():
    if request.method == 'POST':
        tipo_cocina = request.form.get('tipo_cocina')
        ubicacion = request.form.get('ubicacion')
        horario = request.form.get('horario')
        filtros = []
        if tipo_cocina:
            filtros.append(Restaurante.tipo_cocina == tipo_cocina)
        if ubicacion:
            filtros.append(Restaurante.ubicacion == ubicacion)
        if horario:
            filtros.append(Restaurante.horario.contains(horario))
        restaurantes = Restaurante.query.filter(*filtros).all()
    else:
        restaurantes = Restaurante.query.all()
    return render_template('home/buscar_restaurantes.html', restaurantes=restaurantes)

@blueprint.route('/realizar-reserva', methods=['POST'])
def realizar_reserva():
    restaurante = Restaurante.query.get_or_404(id)
    form = ReservaForm()
    if form.validate_on_submit():
        reserva = Reserva(
            id_restaurante=restaurante.id_restaurante,
            dia=form.dia.data,
            hora=form.hora.data,
            mesa=form.mesa.data,
            numero_personas=form.numero_personas.data,
            username=current_user.username
        )
        db.session.add(reserva)
        db.session.commit()
        flash('Reserva realizada con éxito', 'success')
        return redirect(url_for('home.mi_cuenta'))
    return render_template('home/reserva_restaurante.html', restaurante=restaurante, form=form)

@blueprint.route('/mi_cuenta')
#@login_required
def mi_cuenta():
    reservas = Reserva.query.filter_by(username=current_user.username).all()
    return render_template('home/mi_cuenta.html', reservas=reservas)

@blueprint.route('/<template>')
#@login_required
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
    
    
