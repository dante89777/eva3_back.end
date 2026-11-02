"""Catalogo de permisos y servicios utilizados por la API y el cliente web."""

PERMISOS_DEFAULT = [
    {
        'codigo': 'usuarios.ver',
        'nombre': 'Ver usuarios',
        'descripcion': 'Permite consultar el listado de usuarios del sistema.',
    },
    {
        'codigo': 'usuarios.crear',
        'nombre': 'Crear usuarios',
        'descripcion': 'Permite registrar nuevos usuarios en el sistema.',
    },
    {
        'codigo': 'usuarios.actualizar',
        'nombre': 'Actualizar contrasenas',
        'descripcion': 'Permite cambiar la contrasena de un usuario.',
    },
    {
        'codigo': 'permisos.gestionar',
        'nombre': 'Gestionar permisos',
        'descripcion': 'Permite crear permisos y asociarlos a los usuarios.',
    },
    {
        'codigo': 'reportes.ver',
        'nombre': 'Ver reportes',
        'descripcion': 'Permite acceder al modulo de reportes.',
    },
    {
        'codigo': 'configuracion.ver',
        'nombre': 'Ver configuracion',
        'descripcion': 'Permite acceder a la configuracion del sistema.',
    },
]

SERVICIOS = {item['codigo']: item['nombre'] for item in PERMISOS_DEFAULT}


def servicios_de_permisos(codigos):
    """Devuelve los servicios habilitados para una lista de codigos de permiso."""
    return [
        {'codigo': codigo, 'nombre': SERVICIOS.get(codigo, codigo)}
        for codigo in codigos
    ]
