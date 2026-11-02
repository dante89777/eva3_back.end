"""Catalogo de opciones del menu principal y su permiso asociado."""

MENU_SERVICIOS = [
    {
        'permiso': 'usuarios.ver',
        'titulo': 'Usuarios',
        'descripcion': 'Consulta el listado de usuarios registrados en la API.',
        'seccion': 'usuarios',
    },
    {
        'permiso': 'usuarios.crear',
        'titulo': 'Crear usuario',
        'descripcion': 'Registra un nuevo usuario a traves del servicio de la API.',
        'seccion': 'crear-usuario',
    },
    {
        'permiso': 'usuarios.actualizar',
        'titulo': 'Actualizar contrasena',
        'descripcion': 'Cambia la contrasena de un usuario de forma segura.',
        'seccion': 'actualizar',
    },
    {
        'permiso': 'permisos.gestionar',
        'titulo': 'Gestion de permisos',
        'descripcion': 'Crea permisos y asocialos a los usuarios del sistema.',
        'seccion': 'permisos',
    },
    {
        'permiso': 'reportes.ver',
        'titulo': 'Reportes',
        'descripcion': 'Accede al modulo de reportes del sistema.',
        'seccion': 'reportes',
    },
    {
        'permiso': 'configuracion.ver',
        'titulo': 'Configuracion',
        'descripcion': 'Revisa la configuracion general del sistema.',
        'seccion': 'configuracion',
    },
]
