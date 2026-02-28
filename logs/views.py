from rest_framework.views import APIView

from exceptions.generic import GenericException


class ErrorLoggingView(APIView):
    @staticmethod
    def post(request):
        try:
            return 1/0

        except Exception:
            return GenericException(request=request)
