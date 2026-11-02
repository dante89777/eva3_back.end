from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Permiso, Usuario


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion')
    search_fields = ('codigo', 'nombre')


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'nombre_completo', 'is_staff', 'is_active')
    filter_horizontal = ('permisos', 'groups', 'user_permissions')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('nombre_completo', 'permisos')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos adicionales', {'fields': ('email', 'nombre_completo', 'permisos')}),
    )
