from django.contrib.auth.models import AbstractUser
from django.db import models


class Permiso(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Usuario(AbstractUser):
    nombre_completo = models.CharField(max_length=200, blank=True, default='')
    permisos = models.ManyToManyField(
        Permiso,
        blank=True,
        related_name='usuarios',
    )

    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    @property
    def codigos_permisos(self):
        return list(self.permisos.values_list('codigo', flat=True))

    def __str__(self):
        return self.username
