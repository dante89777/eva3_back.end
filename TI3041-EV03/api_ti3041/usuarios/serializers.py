from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Permiso, Usuario


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'codigo', 'nombre', 'descripcion']


class UsuarioSerializer(serializers.ModelSerializer):
    permisos = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'nombre',
            'nombre_completo',
            'is_active',
            'is_staff',
            'permisos',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_permisos(self, obj):
        return obj.codigos_permisos

    def get_nombre(self, obj):
        return obj.nombre_completo or obj.get_full_name() or obj.username


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class RegistroUsuarioSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    nombre_completo = serializers.CharField(
        max_length=200, required=False, allow_blank=True, default=''
    )
    permisos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        write_only=True,
    )

    def validate_username(self, value):
        if Usuario.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('El nombre de usuario ya esta registrado.')
        return value

    def validate_email(self, value):
        if value and Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('El correo electronico ya esta registrado.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_permisos(self, value):
        if not value:
            return []
        encontrados = set(
            Permiso.objects.filter(codigo__in=value).values_list('codigo', flat=True)
        )
        faltantes = sorted(set(value) - encontrados)
        if faltantes:
            raise serializers.ValidationError(
                f'Permisos inexistentes: {", ".join(faltantes)}'
            )
        return value

    def create(self, validated_data):
        codigos = validated_data.pop('permisos', [])
        usuario = Usuario.objects.create_user(**validated_data)
        if codigos:
            usuario.permisos.set(Permiso.objects.filter(codigo__in=codigos))
        return usuario


class ActualizarPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    password_actual = serializers.CharField(
        write_only=True, required=False, trim_whitespace=False
    )
    password_nueva = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_password_nueva(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        actual = attrs.get('password_actual')
        nueva = attrs.get('password_nueva')
        if actual and actual == nueva:
            raise serializers.ValidationError(
                'La nueva contrasena debe ser distinta de la actual.'
            )
        return attrs


class AsociarPermisoSerializer(serializers.Serializer):
    ACCIONES = (('asociar', 'Asociar'), ('quitar', 'Quitar'))

    username = serializers.CharField(max_length=150)
    permiso = serializers.CharField(max_length=100, required=False, write_only=True)
    permisos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        write_only=True,
    )
    accion = serializers.ChoiceField(choices=ACCIONES, default='asociar')

    def validate(self, attrs):
        codigos = list(attrs.get('permisos') or [])
        unico = attrs.get('permiso')
        if unico and unico not in codigos:
            codigos.append(unico)
        if not codigos:
            raise serializers.ValidationError(
                {'permisos': 'Debe indicar al menos un codigo de permiso.'}
            )
        attrs['codigos'] = codigos
        return attrs
