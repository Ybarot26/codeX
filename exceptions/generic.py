import logging

from django.http import JsonResponse

from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger('custom')


class GenericException(JsonResponse):
    """
    Generic Exceptions will return status code of 500 and given error message
    """

    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 request=None,
                 *args,
                 **kwargs):

        if message is None:
            self.message = "There is some internal issue, Please try again later."
        else:
            self.message = message

        self.code = code
        if data is None:
            self.response_data = []

        self.data = {
            "data": self.response_data,
            "status": {
                "code": self.code,
                "message": self.message
            }
        }

        super().__init__(*args, **kwargs, data=self.data)

        request_method = None
        request_url = None

        if self.code == 500 and request:

            if request.method and request.build_absolute_uri():

                request_method = request.method
                request_url = request.build_absolute_uri()

            logger.error(self.message, exc_info=True, extra={
                'status_code': self.code,
                'request_method': request_method,
                'request_url': request_url,
            })


class CustomBadRequest(GenericException):
    def __init__(self, message=None, data=None, code=400, *args, **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = 400

        if message is None:
            self.message = "Bad Request"

        self.status_code = 400


class CustomNotFound(GenericException):
    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_404_NOT_FOUND,
                 *args,
                 **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = status.HTTP_404_NOT_FOUND

        if message is None:
            self.message = "Not Found"

        self.status_code = status.HTTP_404_NOT_FOUND


class CustomAuthenticationFailed(GenericException):
    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_401_UNAUTHORIZED,
                 *args,
                 **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = status.HTTP_401_UNAUTHORIZED

        if message is None:
            self.message = "Unauthorized"

        self.status_code = status.HTTP_401_UNAUTHORIZED


class CustomPermissionDenied(GenericException):
    def __init__(self, message=None,
                 data=None,
                 code=status.HTTP_403_FORBIDDEN,
                 *args,
                 **kwargs):
        super().__init__(message, data, code, *args, **kwargs)

        self.code = status.HTTP_403_FORBIDDEN
        if message is None:
            self.message = "User is not allowed to perform this action"

        self.status_code = status.HTTP_403_FORBIDDEN


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 1400
    default_detail = 'Bad Request'
