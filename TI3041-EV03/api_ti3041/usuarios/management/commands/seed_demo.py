from django.core.management.base import BaseCommand

from usuarios.catalogo import PERMISOS_DEFAULT
from usuarios.models import Permiso, Usuario


class Command(BaseCommand):
    help = 'Crea los permisos base y usuarios de demostracion para la evaluacion.'

    def handle(self, *args, **options):
        permisos = {}
        for item in PERMISOS_DEFAULT:
            permiso, _ = Permiso.objects.update_or_create(
                codigo=item['codigo'],
                defaults={
                    'nombre': item['nombre'],
                    'descripcion': item['descripcion'],
                },
            )
            permisos[item['codigo']] = permiso
        self.stdout.write(self.style.SUCCESS(f'Permisos disponibles: {len(permisos)}'))

        demo, _ = Usuario.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@ti3041.cl',
                'nombre_completo': 'Usuario Demo',
                'is_staff': True,
            },
        )
        demo.email = 'demo@ti3041.cl'
        demo.nombre_completo = 'Usuario Demo'
        demo.is_staff = True
        demo.is_active = True
        demo.set_password('Demo1234!')
        demo.save()
        demo.permisos.set(permisos.values())

        operador, _ = Usuario.objects.get_or_create(
            username='operador',
            defaults={
                'email': 'operador@ti3041.cl',
                'nombre_completo': 'Operador de Consulta',
            },
        )
        operador.email = 'operador@ti3041.cl'
        operador.nombre_completo = 'Operador de Consulta'
        operador.is_active = True
        operador.set_password('Operador1234!')
        operador.save()
        operador.permisos.set([permisos['usuarios.ver'], permisos['reportes.ver']])

        self.stdout.write(self.style.SUCCESS('Usuario demo creado: demo / Demo1234!'))
        self.stdout.write(
            self.style.SUCCESS('Usuario operador creado: operador / Operador1234!')
        )
