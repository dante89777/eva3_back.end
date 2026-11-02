from django.urls import path

from .views import (
    ActualizarPasswordView,
    AddPermisoView,
    AgregarUsuarioView,
    AsociaPermisoView,
    AutentificarView,
    PerfilView,
    UsuarioListView,
    api_root,
)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('autentificar/', AutentificarView.as_view(), name='autentificar'),
    path('agregarusuario/', AgregarUsuarioView.as_view(), name='agregar-usuario'),
    path('actualizar/', ActualizarPasswordView.as_view(), name='actualizar'),
    path('addpermiso/', AddPermisoView.as_view(), name='add-permiso'),
    path('asociapermiso/', AsociaPermisoView.as_view(), name='asocia-permiso'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('usuarios/', UsuarioListView.as_view(), name='usuarios'),
]
