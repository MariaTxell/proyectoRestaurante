# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask_login import login_required
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from apps.home.models import db, Restaurante, Reserva
from apps.authentication.models import Users
from apps.home.forms import ReservaForm
from jinja2 import TemplateNotFound
from sqlalchemy.orm import joinedload
from datetime import datetime


# Ruta para la página de inicio
@blueprint.route('/index')
@login_required
def index():
    restaurantes = Restaurante.query.all()
    
    # Filtrar los restaurantes que tienen reservas este mes
    reservas_por_restaurante = {}
    for restaurante in restaurantes:
        # Cuenta para cada restaurante el numero de reservas que ha tenido este mes
        reservas_del_mes = Reserva.query.filter(
            Reserva.id_restaurante == restaurante.id_restaurante,
            Reserva.dia >= datetime.now().replace(day=1).date()  # Primer día de este mes
        ).count()
        reservas_por_restaurante[restaurante.id_restaurante] = reservas_del_mes
    
    # Ordenar los restaurantes por el número de reservas este mes en orden descendente
    restaurantes_ordenados_por_reservas = sorted(restaurantes, key=lambda x: reservas_por_restaurante.get(x.id_restaurante, 0), reverse=True)
    
    # Obtener los tres primeros restaurantes con el mayor número de reservas este mes
    tres_primeros = restaurantes_ordenados_por_reservas[:3]
    
    return render_template('home/index.html', restaurantes=tres_primeros)

# Ruta para buscar restaurantes
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

@blueprint.route('/horas_disponibles/<int:id_restaurante>')
def horas_disponibles(id_restaurante):
    # Obtener la fecha desde los parámetros de la solicitud
    fecha = request.args.get('fecha')
    
    # Obtener el restaurante por ID, o devolver un error 404 si no se encuentra
    restaurante = Restaurante.query.get_or_404(id_restaurante)
    
    # Obtener todas las horas disponibles del restaurante utilizando la función "obtener_horas_disponibles()"
    horas_disponibles = obtener_horas_disponibles(restaurante.horario)
    
    # Obtener las mesas disponibles para el restaurante en la fecha específica
    mesas_disponibles = obtener_mesas_disponibles(id_restaurante, fecha, None)
    
    # Si no hay ninguna mesa disponible, significa que no se ha hecho ninguna reserva aún para esa fecha a esa hora
    if not mesas_disponibles:
        # Filtrar las horas que ya están reservadas
        reservas = Reserva.query.filter_by(id_restaurante=id_restaurante, dia=fecha).all()
        horas_ocupadas = [reserva.hora.strftime("%H:%M") for reserva in reservas]
        horas_disponibles = [hora for hora in horas_disponibles if hora[0] not in horas_ocupadas]
    
    # Devolver las horas disponibles en formato JSON
    return jsonify({'horas': horas_disponibles})

def obtener_horas_disponibles(tipo_horario):
    # Obtener las horas disponibles según el tipo de horario del restaurante
    if tipo_horario == 'Completo':
        return [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(7, 23)]
    elif tipo_horario == 'Matinal':
        return [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(7, 12)]
    elif tipo_horario == 'Mediodia':
        return [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(12, 16)]
    elif tipo_horario == 'Nocturno':
        return [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(18, 23)]
    return []

@blueprint.route('/mesas_disponibles/<int:id_restaurante>')
def mesas_disponibles(id_restaurante):
    # Obtener la fecha y hora desde los parámetros de la solicitud
    fecha = request.args.get('fecha')
    hora = request.args.get('hora')
    
    # Convertir fecha y hora a los formatos adecuados
    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
    hora = datetime.strptime(hora, "%H:%M").time()
    
    # Obtener las mesas disponibles para el restaurante en la fecha y hora específica, utilizando la función 
    mesas = obtener_mesas_disponibles(id_restaurante, fecha, hora)
    
    # Devolver las mesas disponibles en formato JSON
    return jsonify({'mesas': mesas})

# Función para obtener las mesas disponibles para un restaurante específico en una fecha y hora
def obtener_mesas_disponibles(id_restaurante, fecha, hora):
    # Obtener el restaurante por ID
    restaurante = Restaurante.query.get(id_restaurante)
    if restaurante and fecha:
        # Obtener las reservas existentes para el restaurante en la fecha específica
        reservas = Reserva.query.filter(
            Reserva.id_restaurante == id_restaurante,
            Reserva.dia == fecha,
        ).all()
        
        if hora:
            # Filtrar las reservas que coinciden con la hora específica
            reservas = [reserva for reserva in reservas if reserva.hora == hora]
    
        # Si se ha encontrado alguna reserva
        if reservas:
            # Mesas reservadas en el mismo restaurante
            mesas_reservadas = {reserva.mesa for reserva in reservas}

            # Obtener todas las mesas del restaurante
            todas_mesas = list(range(1, restaurante.numero_mesas + 1))

            # Filtrar mesas disponibles
            mesas_disponibles = [(mesa, f"Mesa {mesa}") for mesa in todas_mesas if mesa not in mesas_reservadas]

            return mesas_disponibles
    # Si no hay reservas para la fecha y hora específicas, mostrar todas las mesas
    return [(mesa, f"Mesa {mesa}") for mesa in range(1, restaurante.numero_mesas + 1)]

# Ruta para realizar una reserva
@blueprint.route('/realizar_reserva/<int:id>', methods=['GET', 'POST'])
@login_required
def realizar_reserva(id):
    # Obtener el restaurante por ID, o devolver un error 404 si no se encuentra
    restaurante = Restaurante.query.get_or_404(id)
    form = ReservaForm()

    # Obtener el usuario actual
    usuario = Users.query.filter_by(username=current_user.username).first()
    
    # Verificar si todos los campos del formulario tienen datos
    if form.dia.data and form.hora.data and form.mesa.data and form.numero_personas.data:
        # Verificar si la fecha de la reserva es una fecha pasada
        if form.dia.data < datetime.now().date():
            flash('No puedes hacer una reserva para una fecha pasada', 'danger')
        else:
            # Crear una nueva instancia de Reserva con los datos del formulario
            reserva = Reserva(
                id_restaurante=restaurante.id_restaurante,
                dia=form.dia.data,
                hora=form.hora.data,
                mesa=form.mesa.data, 
                numero_personas=form.numero_personas.data,
                id_usuario=usuario.id_usuario
            )
            # Añadir la reserva a la sesión de la base de datos y confirmar los cambios
            db.session.add(reserva)
            db.session.commit()
            flash('Reserva realizada con éxito', 'success')
            # Redirigir al usuario a la página de "Mi Cuenta"
            return redirect(url_for('home_blueprint.mi_cuenta'))
    else:
        # Mostrar mensajes de error si hay problemas con el formulario
        flash_errors(form)
    
    # Renderizar la plantilla para la página de "Realizar Reserva"
    return render_template('home/reserva_restaurante.html', restaurante=restaurante, form=form)

# Función para mostrar errores flash en el formulario
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'danger')

# Ruta para cancelar una reserva
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

# Ruta para la página de cuenta del usuario
@blueprint.route('/mi_cuenta')
@login_required
def mi_cuenta():
    # Pasa la fecha actual para poder comprobar si la reserva debe mostrar el boton para cancelar o no
    now = datetime.now()

    # Busca el usuario con el username del usuario registrado actualmente
    usuario = Users.query.filter_by(username=current_user.username).first()

    # Filtra todas las reservas que tienen el mismo id_usuario que el usuario actualmente autenticado (usuario encontrado arriba)
    # Y utiliza joinedload para cargar de forma anticipada la relación restaurante_relacion de cada reserva, para obtener el nombre del restaurante
    reservas = Reserva.query.filter_by(id_usuario=usuario.id_usuario).options(joinedload(Reserva.restaurante_relacion)).all()
    return render_template('home/mi_cuenta.html', now=now, reservas=reservas)

# Ruta para la página de contacto
@blueprint.route('/contacto')
@login_required
def contacto():
    usuario = Users.query.filter_by(username=current_user.username).first()
    return render_template('home/contacto.html', usuario=usuario) # Pasa el usuario para poner automaticamente el correo del usuario autenticado

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
    
    
