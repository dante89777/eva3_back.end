from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .catalogo import servicios_de_permisos
from .models import Permiso, Usuario
from .serializers import (
    ActualizarPasswordSerializer,
    AsociarPermisoSerializer,
    LoginSerializer,
    PermisoSerializer,
    RegistroUsuarioSerializer,
    UsuarioSerializer,
)


def datos_usuario(usuario):
    return UsuarioSerializer(usuario).data


def datos_sesion(usuario, access=None, refresh=None):
    codigos = usuario.codigos_permisos
    data = {
        'usuario': datos_usuario(usuario),
        'permisos': codigos,
        'servicios': servicios_de_permisos(codigos),
    }
    if access is not None:
        data['access'] = access
    if refresh is not None:
        data['refresh'] = refresh
        data['token_type'] = 'Bearer'
    return data


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response(
        {
            'success': True,
            'message': 'API TI3041 - Evaluacion Practica 03',
            'endpoints': {
                'autentificar': request.build_absolute_uri('/api/autentificar/'),
                'agregarusuario': request.build_absolute_uri('/api/agregarusuario/'),
                'actualizar': request.build_absolute_uri('/api/actualizar/'),
                'addpermiso': request.build_absolute_uri('/api/addpermiso/'),
                'asociapermiso': request.build_absolute_uri('/api/asociapermiso/'),
                'perfil': request.build_absolute_uri('/api/perfil/'),
                'permisos': request.build_absolute_uri('/api/permisos/'),
            },
        }
    )


class AutentificarView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = authenticate(
            request=request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if usuario is None or not usuario.is_active:
            return Response(
                {
                    'success': False,
                    'message': 'Usuario o contrasena incorrectos.',
                    'errores': {'credenciales': 'No fue posible autenticar al usuario.'},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(usuario)
        access = refresh.access_token
        for token in (refresh, access):
            token['username'] = usuario.username
            token['permisos'] = usuario.codigos_permisos

        data = datos_sesion(usuario, access=str(access), refresh=str(refresh))
        return Response(
            {
                'success': True,
                'message': 'Autenticacion exitosa.',
                'data': data,
            }
        )


class AgregarUsuarioView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Usuario creado correctamente.',
                'data': datos_usuario(usuario),
            },
            status=status.HTTP_201_CREATED,
        )


class ActualizarPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self._actualizar(request)

    def put(self, request):
        return self._actualizar(request)

    def patch(self, request):
        return self._actualizar(request)

    def _actualizar(self, request):
        serializer = ActualizarPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username') or request.user.username
        es_otro_usuario = username.lower() != request.user.username.lower()

        if es_otro_usuario and not request.user.is_staff:
            return Response(
                {
                    'success': False,
                    'message': 'No tiene autorizacion para cambiar la contrasena de otro usuario.',
                    'errores': {'permiso': 'Solo un administrador puede realizar esta accion.'},
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        usuario = Usuario.objects.filter(username__iexact=username).first()
        if usuario is None:
            return Response(
                {
                    'success': False,
                    'message': 'El usuario indicado no existe.',
                    'errores': {'username': 'Usuario inexistente.'},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not es_otro_usuario:
            password_actual = serializer.validated_data.get('password_actual')
            if not password_actual:
                return Response(
                    {
                        'success': False,
                        'message': 'Debe indicar la contrasena actual.',
                        'errores': {'password_actual': 'Este campo es obligatorio.'},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not usuario.check_password(password_actual):
                return Response(
                    {
                        'success': False,
                        'message': 'La contrasena actual no es correcta.',
                        'errores': {'password_actual': 'Contrasena invalida.'},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        usuario.set_password(serializer.validated_data['password_nueva'])
        usuario.save(update_fields=['password'])

        return Response(
            {
                'success': True,
                'message': 'Contrasena actualizada correctamente.',
                'data': {'username': usuario.username},
            }
        )


class AddPermisoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permisos = Permiso.objects.all()
        return Response(
            {
                'success': True,
                'message': 'Listado de permisos del sistema.',
                'data': PermisoSerializer(permisos, many=True).data,
            }
        )

    def post(self, request):
        codigo = str(request.data.get('codigo', '')).strip()
        nombre = str(request.data.get('nombre', '')).strip()
        descripcion = str(request.data.get('descripcion', '')).strip()

        errores = {}
        if not codigo:
            errores['codigo'] = 'Este campo es obligatorio.'
        if not nombre:
            errores['nombre'] = 'Este campo es obligatorio.'
        if errores:
            return Response(
                {
                    'success': False,
                    'message': 'Datos incompletos.',
                    'errores': errores,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Permiso.objects.filter(codigo__iexact=codigo).exists():
            return Response(
                {
                    'success': False,
                    'message': 'El permiso ya existe.',
                    'errores': {'codigo': 'Codigo de permiso duplicado.'},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        permiso = Permiso.objects.create(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
        )
        return Response(
            {
                'success': True,
                'message': 'Permiso creado correctamente.',
                'data': PermisoSerializer(permiso).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AsociaPermisoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AsociarPermisoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        usuario = Usuario.objects.filter(username__iexact=datos['username']).first()
        if usuario is None:
            return Response(
                {
                    'success': False,
                    'message': 'El usuario indicado no existe.',
                    'errores': {'username': 'Usuario inexistente.'},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        permisos = list(Permiso.objects.filter(codigo__in=datos['codigos']))
        encontrados = {permiso.codigo for permiso in permisos}
        faltantes = sorted(set(datos['codigos']) - encontrados)
        if faltantes:
            return Response(
                {
                    'success': False,
                    'message': 'Uno o mas permisos no existen.',
                    'errores': {'permisos': f'Permisos inexistentes: {", ".join(faltantes)}'},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if datos['accion'] == 'quitar':
            usuario.permisos.remove(*permisos)
            mensaje = 'Permisos desasociados correctamente.'
        else:
            usuario.permisos.add(*permisos)
            mensaje = 'Permisos asociados correctamente.'

        return Response(
            {
                'success': True,
                'message': mensaje,
                'data': datos_usuario(usuario),
            }
        )


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                'success': True,
                'message': 'Perfil del usuario autenticado.',
                'data': datos_sesion(request.user),
            }
        )


class UsuarioListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = Usuario.objects.prefetch_related('permisos').order_by('username')
        return Response(
            {
                'success': True,
                'message': 'Listado de usuarios.',
                'data': UsuarioSerializer(usuarios, many=True).data,
            }
        )
