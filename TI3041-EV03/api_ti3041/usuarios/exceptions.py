import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _mensaje_principal(detalle):
    if isinstance(detalle, dict):
        if 'detail' in detalle:
            return str(detalle['detail'])
        return 'Error de validacion en los datos enviados.'
    if isinstance(detalle, list):
        return 'Error de validacion en los datos enviados.'
    return str(detalle)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.exception('Error no controlado en la API', exc_info=exc)
        return Response(
            {
                'success': False,
                'message': 'Error interno del servidor.',
                'errores': {'detalle': 'Ocurrio un error inesperado.'},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response.data = {
        'success': False,
        'message': _mensaje_principal(response.data),
        'errores': response.data,
    }
    return response
