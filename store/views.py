from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password

from rest_framework.views import APIView

from email_validator import validate_email, EmailNotValidError


from common.constants import (
    AUTHORIZATION_HEADER_MISSING,
    BAD_REQUEST,
    DATA_IS_INVALID,
    EMAIL_IS_INVALID,
    INCORRECT_PASSWORD,
    STORE_REGISTERED_SUCCESSFULLY,
    USER_ALREADY_EXISTS,
    USER_LOGGED_IN_SUCCESSFULLY,
    USER_NOT_FOUND,
    STORE_REGISTERED_SUCCESSFULLY,
    STORE_LOGGED_OUT_SUCCESSFULLY
)
from common.helpers import validate_password

from store.models import Store
from store.serializers import StoreRegistrationSerializer

from exceptions.generic_response import GenericSuccessResponse
from exceptions.generic import CustomBadRequest, CustomNotFound, GenericException

from security.store_authorization import StoreJWTAuthentication, get_store_authentication_token, save_token
from security.models import StoreAuthTokens


class Registration(APIView):
    def post(self, request):
        try:

            if (
                "store_email" not in request.data or request.data["store_email"] == "" or
                "store_password" not in request.data or request.data["store_password"] == "" or
                "store_address" not in request.data or request.data["store_address"] == "" or
                "store_name" not in request.data or request.data["store_name"] == ""

            ):
                return CustomBadRequest(message=BAD_REQUEST)

            email_validation = validate_email(request.data['store_email'])

            password_validation_response = validate_password(
                request.data["store_password"])

            if password_validation_response:
                return password_validation_response

            if Store.objects.filter(store_email=request.data['store_email']):
                return CustomBadRequest(message=USER_ALREADY_EXISTS)

            registration_serializer = StoreRegistrationSerializer(
                data=request.data)

            # Hash the password before saving
            request.data["store_password"] = make_password(
                request.data["store_password"])

            if registration_serializer.is_valid():
                store = registration_serializer.save()
                tokens = get_store_authentication_token(store)
                save_token(tokens)

                # Uncomment the line below to send a registration email

                # message = f"Hi {store.store_name},\n\nThank you for registering on our platform. We're excited to have you!\n\nBest Regards,\CodeX Team"
                # send_registration_email(store.store_email, store.store_name, message=message)

                return GenericSuccessResponse(tokens, message=STORE_REGISTERED_SUCCESSFULLY, status=201)

            return CustomBadRequest(message=DATA_IS_INVALID)

        except EmailNotValidError as e:

            # For exact error message
            # return CustomBadRequest(message=str(e))

            return CustomBadRequest(message=EMAIL_IS_INVALID)

        except Exception:
            return GenericException(request=request)


class Logout(APIView):
    authentication_classes = [StoreJWTAuthentication]

    def delete(self, request):

        try:
            header = request.headers.get("authorization")
            if not header:
                return CustomBadRequest(message=AUTHORIZATION_HEADER_MISSING)

            token = header.split(" ")[1]

            StoreAuthTokens.objects.filter(
                Q(access_token=token) | Q(refresh_token=token)).delete()

            return GenericSuccessResponse(message=STORE_LOGGED_OUT_SUCCESSFULLY, status=204)

        except Exception:
            return GenericException(request=request)


class Login(APIView):
    def post(self, request):
        try:

            if (
                "store_email" not in request.data or request.data["store_email"] == "" or
                "store_password" not in request.data or request.data["store_password"] == ""
            ):
                return CustomBadRequest(BAD_REQUEST)

            email = request.data.get("store_email")
            password = request.data.get("store_password")

            if not email or not password:
                return CustomBadRequest(message=BAD_REQUEST)
            validation = validate_email(email)

            store = Store.objects.get(store_email=email, is_deleted=False)

            if not check_password(password, store.store_password):
                return CustomBadRequest(message=INCORRECT_PASSWORD)

            authentication_tokens = get_store_authentication_token(store)
            save_token(authentication_tokens)
            return GenericSuccessResponse(authentication_tokens, message=USER_LOGGED_IN_SUCCESSFULLY, status=201)

        except EmailNotValidError as e:
            return CustomBadRequest(message=str(e))

        except Store.DoesNotExist:
            return CustomNotFound(message=USER_NOT_FOUND)

        except Exception:
            return GenericException(request=request)
