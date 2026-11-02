import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse

from .menu import MENU_SERVICIOS

CLAVES_SESION = ('access', 'refresh', 'usuario', 'permisos', 'servicios')


def _url_api(ruta):
    return f"{settings.API_BASE_URL.rstrip('/')}/{ruta.lstrip('/')}"


def _limpiar_sesion(request):
    for clave in CLAVES_SESION:
        request.session.pop(clave, None)


def _guardar_sesion(request, data):
    request.session['access'] = data.get('access', '')
    request.session['refresh'] = data.get('refresh', '')
    request.session['usuario'] = data.get('usuario', {})
    request.session['permisos'] = data.get('permisos', [])
    request.session['servicios'] = data.get('servicios', [])


def _flash(request, tipo, mensaje):
    request.session['flash'] = {'tipo': tipo, 'mensaje': mensaje}
    request.session.modified = True


def _mensaje_error(data):
    mensaje = data.get('message') or 'La operacion no se pudo completar.'
    errores = data.get('errores')
    partes = []
    if isinstance(errores, dict):
        for campo, valor in errores.items():
            if isinstance(valor, (list, tuple)):
                texto = ', '.join(str(item) for item in valor)
            else:
                texto = str(valor)
            partes.append(f'{campo}: {texto}')
    elif errores:
        partes.append(str(errores))
    if partes:
        mensaje = f"{mensaje} ({'; '.join(partes)})"
    return mensaje


def _llamar_api(request, metodo, ruta, **kwargs):
    headers = kwargs.pop('headers', {})
    token = request.session.get('access')
    if token:
        headers.setdefault('Authorization', f'Bearer {token}')
    try:
        respuesta = requests.request(
            metodo,
            _url_api(ruta),
            headers=headers,
            timeout=settings.API_TIMEOUT,
            **kwargs,
        )
    except requests.RequestException:
        return None, {
            'success': False,
            'message': 'No fue posible conectar con la API.',
        }
    try:
        data = respuesta.json()
    except ValueError:
        data = {
            'success': False,
            'message': 'La API respondio con un formato invalido.',
        }
    return respuesta.status_code, data


def _redirigir_login_expirado():
    return redirect(f"{reverse('login')}?expirado=1")


def _cargar_usuarios(request):
    status, data = _llamar_api(request, 'GET', 'usuarios/')
    if status == 200:
        return data.get('data', []), None
    return [], _mensaje_error(data)


def _cargar_permisos(request):
    status, data = _llamar_api(request, 'GET', 'addpermiso/')
    if status == 200:
        return data.get('data', []), None
    return [], _mensaje_error(data)


def login_view(request):
    if request.session.get('access') and request.method == 'GET':
        return redirect('dashboard')

    error = None
    username = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error = 'Debe completar el usuario y la contrasena.'
        else:
            try:
                respuesta = requests.post(
                    _url_api('autentificar/'),
                    json={'username': username, 'password': password},
                    timeout=settings.API_TIMEOUT,
                )
            except requests.RequestException:
                error = (
                    'No fue posible conectar con la API. '
                    'Verifique que el Proyecto 1 este en ejecucion.'
                )
            else:
                if respuesta.status_code == 200:
                    try:
                        data = respuesta.json().get('data', {})
                    except ValueError:
                        error = 'La API respondio con un formato invalido.'
                    else:
                        _guardar_sesion(request, data)
                        return redirect('dashboard')
                elif respuesta.status_code == 401:
                    error = 'Usuario o contrasena incorrectos.'
                else:
                    try:
                        error = respuesta.json().get(
                            'message', 'La API rechazo la solicitud.'
                        )
                    except ValueError:
                        error = 'La API rechazo la solicitud.'

    if request.GET.get('expirado'):
        error = 'La sesion expiro. Inicie sesion nuevamente.'

    return render(
        request,
        'web/login.html',
        {'error': error, 'username': username, 'api_base': settings.API_BASE_URL},
    )


def dashboard_view(request):
    access = request.session.get('access')
    if not access:
        return redirect('login')

    avisos = []
    usuario = request.session.get('usuario', {})
    permisos = request.session.get('permisos', [])

    try:
        respuesta = requests.get(
            _url_api('perfil/'),
            headers={'Authorization': f'Bearer {access}'},
            timeout=settings.API_TIMEOUT,
        )
    except requests.RequestException:
        avisos.append('No se pudo actualizar la informacion desde la API.')
    else:
        if respuesta.status_code == 401:
            _limpiar_sesion(request)
            return _redirigir_login_expirado()
        if respuesta.status_code == 200:
            try:
                data = respuesta.json().get('data', {})
            except ValueError:
                avisos.append('La API respondio con un formato invalido.')
            else:
                usuario = data.get('usuario', usuario)
                permisos = data.get('permisos', permisos)
                request.session['usuario'] = usuario
                request.session['permisos'] = permisos
                request.session['servicios'] = data.get('servicios', [])
        else:
            avisos.append('La API no entrego el perfil del usuario autenticado.')

    menu = [item for item in MENU_SERVICIOS if item['permiso'] in permisos]
    secciones = {item['seccion']: item for item in menu}

    seccion_solicitada = request.GET.get('seccion')
    if seccion_solicitada and seccion_solicitada not in secciones:
        _flash(request, 'error', 'No tiene permisos para acceder a esa seccion.')
        return redirect('dashboard')

    seccion_actual = secciones.get(seccion_solicitada)
    usuarios = []
    permisos_list = []

    if seccion_actual:
        clave = seccion_actual['seccion']
        if clave in ('usuarios', 'actualizar', 'asociar-permiso'):
            usuarios, error = _cargar_usuarios(request)
            if error:
                avisos.append(error)
        if clave in ('crear-usuario', 'permisos', 'configuracion'):
            permisos_list, error = _cargar_permisos(request)
            if error:
                avisos.append(error)
        if clave in ('permisos', 'reportes'):
            usuarios, error = _cargar_usuarios(request)
            if error:
                avisos.append(error)
        if clave == 'reportes':
            permisos_list, error = _cargar_permisos(request)
            if error:
                avisos.append(error)

    flash = request.session.pop('flash', None)
    request.session.modified = True

    contexto = {
        'usuario': usuario,
        'permisos': permisos,
        'menu': menu,
        'seccion_actual': seccion_actual,
        'plantilla': (
            f"web/secciones/{seccion_actual['seccion']}.html"
            if seccion_actual
            else None
        ),
        'usuarios': usuarios,
        'permisos_list': permisos_list,
        'avisos': avisos,
        'flash': flash,
        'api_base': settings.API_BASE_URL,
    }

    if seccion_actual and seccion_actual['seccion'] == 'reportes':
        contexto['total_asociaciones'] = sum(
            len(item.get('permisos', [])) for item in usuarios
        )
        contexto['usuarios_sin_permisos'] = sum(
            1 for item in usuarios if not item.get('permisos')
        )

    return render(request, 'web/dashboard.html', contexto)


def logout_view(request):
    _limpiar_sesion(request)
    request.session.flush()
    return redirect('login')


def _requiere_sesion(request):
    return bool(request.session.get('access'))


def _tiene_permiso(request, codigo):
    return codigo in request.session.get('permisos', [])


def crear_usuario_view(request):
    if request.method != 'POST':
        return redirect('dashboard')
    if not _requiere_sesion(request):
        return redirect('login')
    if not _tiene_permiso(request, 'usuarios.crear'):
        _flash(request, 'error', 'No tiene permiso para crear usuarios.')
        return redirect('dashboard')

    datos = {
        'username': request.POST.get('username', '').strip(),
        'password': request.POST.get('password', ''),
        'email': request.POST.get('email', '').strip(),
        'nombre_completo': request.POST.get('nombre_completo', '').strip(),
        'permisos': request.POST.getlist('permisos'),
    }
    status, data = _llamar_api(request, 'POST', 'agregarusuario/', json=datos)

    if status == 401:
        _limpiar_sesion(request)
        return _redirigir_login_expirado()

    if status in (200, 201):
        _flash(request, 'success', 'Usuario creado correctamente.')
    else:
        _flash(request, 'error', _mensaje_error(data))
    return redirect(f"{reverse('dashboard')}?seccion=crear-usuario")


def actualizar_password_view(request):
    if request.method != 'POST':
        return redirect('dashboard')
    if not _requiere_sesion(request):
        return redirect('login')

    usuario_sesion = request.session.get('usuario', {})
    username = request.POST.get('username', '').strip()
    if not usuario_sesion.get('is_staff') or not username:
        username = usuario_sesion.get('username', '')

    datos = {
        'username': username,
        'password_nueva': request.POST.get('password_nueva', ''),
    }
    password_actual = request.POST.get('password_actual', '')
    if password_actual:
        datos['password_actual'] = password_actual

    status, data = _llamar_api(request, 'PUT', 'actualizar/', json=datos)

    if status == 401:
        _limpiar_sesion(request)
        return _redirigir_login_expirado()

    if status == 200:
        _flash(request, 'success', 'Contrasena actualizada correctamente.')
    else:
        _flash(request, 'error', _mensaje_error(data))
    return redirect(f"{reverse('dashboard')}?seccion=actualizar")


def crear_permiso_view(request):
    if request.method != 'POST':
        return redirect('dashboard')
    if not _requiere_sesion(request):
        return redirect('login')
    if not _tiene_permiso(request, 'permisos.gestionar'):
        _flash(request, 'error', 'No tiene permiso para crear permisos.')
        return redirect('dashboard')

    datos = {
        'codigo': request.POST.get('codigo', '').strip(),
        'nombre': request.POST.get('nombre', '').strip(),
        'descripcion': request.POST.get('descripcion', '').strip(),
    }
    status, data = _llamar_api(request, 'POST', 'addpermiso/', json=datos)

    if status == 401:
        _limpiar_sesion(request)
        return _redirigir_login_expirado()

    if status == 201:
        _flash(request, 'success', 'Permiso creado correctamente.')
    else:
        _flash(request, 'error', _mensaje_error(data))
    return redirect(f"{reverse('dashboard')}?seccion=permisos")


def asociar_permiso_view(request):
    if request.method != 'POST':
        return redirect('dashboard')
    if not _requiere_sesion(request):
        return redirect('login')
    if not _tiene_permiso(request, 'permisos.gestionar'):
        _flash(request, 'error', 'No tiene permiso para gestionar permisos.')
        return redirect('dashboard')

    permisos = request.POST.getlist('permisos')
    if not permisos:
        _flash(request, 'error', 'Debe seleccionar al menos un permiso.')
        return redirect(f"{reverse('dashboard')}?seccion=permisos")

    accion = request.POST.get('accion', 'asociar')
    if accion not in ('asociar', 'quitar'):
        accion = 'asociar'

    datos = {
        'username': request.POST.get('username', '').strip(),
        'permisos': permisos,
        'accion': accion,
    }
    status, data = _llamar_api(request, 'POST', 'asociapermiso/', json=datos)

    if status == 401:
        _limpiar_sesion(request)
        return _redirigir_login_expirado()

    if status == 200:
        texto = (
            'Permisos asociados correctamente.'
            if accion == 'asociar'
            else 'Permisos desasociados correctamente.'
        )
        _flash(request, 'success', texto)
    else:
        _flash(request, 'error', _mensaje_error(data))
    return redirect(f"{reverse('dashboard')}?seccion=permisos")
