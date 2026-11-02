from django.urls import path

from .views import (
    actualizar_password_view,
    asociar_permiso_view,
    crear_permiso_view,
    crear_usuario_view,
    dashboard_view,
    login_view,
    logout_view,
)

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('acciones/crear-usuario/', crear_usuario_view, name='accion-crear-usuario'),
    path(
        'acciones/actualizar-password/',
        actualizar_password_view,
        name='accion-actualizar-password',
    ),
    path('acciones/crear-permiso/', crear_permiso_view, name='accion-crear-permiso'),
    path(
        'acciones/asociar-permiso/',
        asociar_permiso_view,
        name='accion-asociar-permiso',
    ),
]
