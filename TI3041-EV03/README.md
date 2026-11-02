# TI3041 - Evaluación Práctica 03

Implementación de la Evaluación Práctica 03 de **Programación Back End** (INACAP),
compuesta por dos proyectos Django:

1. **`api_ti3041`**: API RESTful con Django REST Framework, autenticación **JWT** y
   persistencia en **SQLite**.
2. **`cliente_ti3041`**: sistema de información con **login**, página principal y
   **menú dinámico** construido según los permisos retornados por la API.

El cliente web **no utiliza base de datos**, no usa el admin de Django y no usa
formularios automáticos: los formularios HTML están escritos manualmente y la
sesión se guarda en una cookie firmada.

---

## 1. Estructura del proyecto

```text
TI3041-EV03/
├── api_ti3041/                 # Proyecto 1 - API REST
│   ├── api_ti3041/             # Configuración Django
│   ├── usuarios/               # App: modelos, serializers, vistas, permisos
│   │   ├── management/commands/seed_demo.py
│   │   ├── catalogo.py
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── db.sqlite3              # Base de datos SQLite (datos demo incluidos)
│   ├── manage.py
│   └── requirements.txt
├── cliente_ti3041/             # Proyecto 2 - Cliente web
│   ├── cliente_ti3041/         # Configuración Django (sin BD)
│   ├── web/
│   │   ├── static/web/estilos.css
│   │   ├── templates/web/
│   │   │   ├── base.html
│   │   │   ├── login.html
│   │   │   ├── dashboard.html
│   │   │   └── secciones/
│   │   │       ├── usuarios.html
│   │   │       ├── crear-usuario.html
│   │   │       ├── actualizar.html
│   │   │       ├── permisos.html
│   │   │       ├── reportes.html
│   │   │       └── configuracion.html
│   │   ├── menu.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── manage.py
│   └── requirements.txt
├── .vscode/tasks.json          # Tareas para ejecutar ambos proyectos
└── README.md
```

---

## 2. Requisitos

- Python 3.13
- Dependencias del Proyecto 1: `Django`, `djangorestframework`,
  `djangorestframework-simplejwt`
- Dependencias del Proyecto 2: `Django`, `requests`

Instalación:

```powershell
python -m pip install -r api_ti3041\requirements.txt
python -m pip install -r cliente_ti3041\requirements.txt
```

---

## 3. Ejecución

### Opción A: desde VS Code

1. Abrir la carpeta `TI3041-EV03` en VS Code.
2. Presionar `Ctrl + Shift + B` y elegir **Ejecutar ambos proyectos**.
3. Abrir <http://127.0.0.1:8001/> en el navegador.

### Opción B: dos terminales

Terminal 1 (API):

```powershell
cd api_ti3041
python manage.py runserver 127.0.0.1:8000
```

Terminal 2 (cliente):

```powershell
cd cliente_ti3041
python manage.py runserver 127.0.0.1:8001
```

- Cliente web: <http://127.0.0.1:8001/>
- API navegable: <http://127.0.0.1:8000/api/>

Si la API se ejecuta en otra dirección:

```powershell
$env:API_BASE_URL = "http://127.0.0.1:8000/api"
python manage.py runserver 127.0.0.1:8001
```

### Credenciales de demostración

| Usuario    | Contraseña      | Permisos                                      |
|------------|-----------------|-----------------------------------------------|
| `demo`     | `Demo1234!`     | Todos (6)                                     |
| `operador` | `Operador1234!` | `usuarios.ver`, `reportes.ver`                |

Los datos se regeneran con:

```powershell
cd api_ti3041
python manage.py seed_demo
```

---

## 4. Endpoints del Proyecto 1

Base: `http://127.0.0.1:8000/api/`

| Método | Endpoint             | Autenticación | Descripción |
|--------|----------------------|---------------|-------------|
| POST   | `autentificar/`      | No            | Valida usuario/contraseña y retorna JWT + permisos + servicios. |
| POST   | `agregarusuario/`    | No            | Crea un nuevo usuario. |
| PUT/PATCH | `actualizar/`     | JWT           | Cambia la contraseña del usuario autenticado (o de otro usuario si es staff). |
| GET/POST | `addpermiso/`      | JWT           | Lista o crea permisos del sistema. |
| POST   | `asociapermiso/`     | JWT           | Asocia o quita permisos a un usuario. |
| GET    | `perfil/`            | JWT           | Retorna usuario, permisos y servicios del token actual. |
| GET    | `usuarios/`          | JWT           | Lista los usuarios registrados. |

### Formato de respuesta

Éxito:

```json
{
  "success": true,
  "message": "Autenticacion exitosa.",
  "data": {
    "access": "<jwt>",
    "refresh": "<jwt>",
    "token_type": "Bearer",
    "usuario": { "id": 1, "username": "demo", "permisos": ["usuarios.ver"] },
    "permisos": ["usuarios.ver", "reportes.ver"],
    "servicios": [
      { "codigo": "usuarios.ver", "nombre": "Ver usuarios" }
    ]
  }
}
```

Error:

```json
{
  "success": false,
  "message": "Usuario o contrasena incorrectos.",
  "errores": { "credenciales": "No fue posible autenticar al usuario." }
}
```

### Ejemplos con PowerShell

Autenticarse:

```powershell
$login = Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/autentificar/" `
  -ContentType "application/json" `
  -Body '{"username":"demo","password":"Demo1234!"}'

$token = $login.data.access
$headers = @{ Authorization = "Bearer $token" }
```

Crear usuario:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/agregarusuario/" `
  -ContentType "application/json" `
  -Body '{"username":"nuevo","password":"Nuevo1234!","email":"nuevo@ti3041.cl","nombre_completo":"Nuevo Usuario"}'
```

Crear y asociar permiso:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/addpermiso/" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"codigo":"ventas.ver","nombre":"Ver ventas","descripcion":"Acceso al modulo de ventas"}'

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/asociapermiso/" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"username":"nuevo","permisos":["ventas.ver","reportes.ver"]}'
```

Actualizar contraseña:

```powershell
Invoke-RestMethod -Method Put `
  -Uri "http://127.0.0.1:8000/api/actualizar/" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"password_actual":"Demo1234!","password_nueva":"Demo5678!"}'
```

---

## 5. Funcionamiento del Proyecto 2

1. El usuario ingresa sus credenciales en el login.
2. La vista `login_view` envía `username` y `password` al endpoint
   `autentificar/` mediante `requests`.
3. La API responde con el JWT, los datos del usuario, sus permisos y servicios.
4. El cliente guarda el JWT y los permisos en una cookie de sesión firmada.
5. En el panel principal, `dashboard_view` vuelve a consultar `perfil/` con el
   token para refrescar los permisos.
6. El menú se construye filtrando `MENU_SERVICIOS` con los códigos de permiso
   retornados por la API. Un usuario sin permiso no ve la opción.
7. Cada opción del menú abre una pantalla funcional que consume la API.

### Pantallas del cliente

| Ruta | Función | Permiso requerido |
|------|---------|-------------------|
| `/login/` | Formulario de acceso que consume `autentificar/`. | No |
| `/dashboard/` | Página principal con menú dinámico y permisos. | Sesión activa |
| `/dashboard/?seccion=usuarios` | Listado de usuarios desde `GET /usuarios/`. | `usuarios.ver` |
| `/dashboard/?seccion=crear-usuario` | Formulario para crear usuarios. | `usuarios.crear` |
| `/dashboard/?seccion=actualizar` | Cambio de contraseña. | `usuarios.actualizar` |
| `/dashboard/?seccion=permisos` | Crear permisos y asociarlos a usuarios. | `permisos.gestionar` |
| `/dashboard/?seccion=reportes` | Resumen de usuarios, permisos y accesos. | `reportes.ver` |
| `/dashboard/?seccion=configuracion` | Datos de sesión, API y arquitectura. | `configuracion.ver` |
| `/acciones/crear-usuario/` | Procesa el formulario de creación. | `usuarios.crear` |
| `/acciones/actualizar-password/` | Procesa el cambio de contraseña. | Sesión / `usuarios.actualizar` |
| `/acciones/crear-permiso/` | Procesa la creación de permisos. | `permisos.gestionar` |
| `/acciones/asociar-permiso/` | Procesa la asociación o desasociación. | `permisos.gestionar` |

Las acciones verifican los permisos de la sesión y la API vuelve a validar el
JWT. Los resultados se muestran como mensajes de éxito o error en la pantalla.

### Prueba sugerida

- Ingresar con `demo`: se muestran las 6 opciones del menú.
- Abrir **Usuarios** y verificar el listado obtenido desde la API.
- Crear un usuario, asignarle permisos y luego cambiar su contraseña.
- Crear un permiso y asociarlo o quitarlo desde **Gestión de permisos**.
- Cerrar sesión e ingresar con `operador`: solo se muestran **Usuarios** y
  **Reportes**; si intenta abrir otra sección por URL, el sistema la bloquea.

---

## 6. Relación con la pauta de evaluación

| Criterio | Implementación |
|----------|----------------|
| 1. Endpoint `autentificar` | `AutentificarView` valida credenciales con `authenticate`, genera JWT y retorna JSON con usuario, permisos y servicios. |
| 2. `agregarusuario` y `actualizar` | Registro con contraseña hasheada y validadores; cambio de contraseña con verificación de la actual y restricción para modificar otros usuarios. |
| 3. `addpermiso` y `asociapermiso` | Verificación de duplicados, validación de permisos existentes, asociación/desasociación idempotente. |
| 4. Persistencia SQLite | Modelos `Usuario` y `Permiso` con relación ManyToMany en `api_ti3041/db.sqlite3`. |
| 5. Login y consumo de API | `login_view` consume `autentificar/`; el panel valida el token contra `perfil/` y cada pantalla consume su endpoint. |
| 6. Menú dinámico | `dashboard_view` filtra las opciones según los permisos devueltos por la API; las secciones no autorizadas se bloquean. |
| 7. Restricciones técnicas | Proyecto 2 sin base de datos, sin admin, sin formularios automáticos y sin dependencias innecesarias. |

---

## 7. Consideraciones de seguridad

- Las contraseñas se almacenan con el hashing de Django (`set_password`).
- La nueva contraseña pasa por `AUTH_PASSWORD_VALIDATORS`.
- Los endpoints de gestión requieren JWT; el token expira a los 60 minutos.
- Los errores de autenticación no revelan si el usuario existe.
- `agregarusuario` queda abierto para permitir el registro inicial. En un entorno
  productivo debería restringirse (por ejemplo, solo administradores) y agregar
  limitación de intentos de login, HTTPS y `DEBUG = False`.
- Las claves `SECRET_KEY` incluidas son de desarrollo; deben reemplazarse en
  producción.

---

**Asignatura:** TI3041 - Programación Back End  
**Evaluación:** Práctica 03 - Unidad 3: API RESTful con integración a base de datos
