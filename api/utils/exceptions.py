from collections import OrderedDict

from rest_framework import status as drf_status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = OrderedDict((
            ('status_code', exc.status_code),
            ('message', response.status_text),
            ('errors', [exc.detail])
        ))
    else:
        data = OrderedDict((
            ('status_code', drf_status.HTTP_500_INTERNAL_SERVER_ERROR),
            ('message', 'Internal server error')
        ))
        response = Response(data=data, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(exc, context)

    return response


class ResourceNotFoundException(APIException):
    """Exception is raised when resource is not found."""
    status_code = drf_status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'not_found'
    data = {
        'status_code': drf_status.HTTP_404_NOT_FOUND,
        'message': default_detail
    }