import traceback

from django.contrib.auth.hashers import make_password
import hashlib
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password

from rest_framework.views import APIView

from email_validator import validate_email, EmailNotValidError


from common.constants import (
    AUTHORIZATION_HEADER_MISSING,
    BAD_REQUEST,
    DATA_IS_INVALID,
    DATA_NOT_FOUND,
    EMAIL_IS_INVALID,
    EMAIL_IS_NOT_AVAILABLE,
    FETCHED_STORE_DATA_SUCCESFULLY,
    INCORRECT_PASSWORD,
    STORE_DETAILS_UPDATED_SUCCESSFULLY,
    STORE_REGISTERED_SUCCESSFULLY,
    USER_ALREADY_EXISTS,
    USER_DOES_NOT_EXIST,
    USER_LOGGED_IN_SUCCESSFULLY,
    USER_NOT_FOUND,
    STORE_REGISTERED_SUCCESSFULLY,
    STORE_LOGGED_OUT_SUCCESSFULLY
)
from common.helpers import send_registration_email, validate_password

from employee.models import Employee
from employee.serializers import (EmployeeDetailsManagementSerializer,
                                  EmployeeRegistrationSerializer,
                                  FetchEmployeeDetailsSerializer)
from store.helpers import update_store_services, updpate_store_langauges
from store.models import Store
from store.serializers import StoreDetailsManagementSerializer, StoreRegistrationSerializer

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
                # "store_address" not in request.data or request.data["store_address"] == "" or
                "store_name" not in request.data or request.data["store_name"] == ""

            ):
                return CustomBadRequest(message=BAD_REQUEST)

            email_validation = validate_email(request.data['store_email'])

            password_validation_response = validate_password(
                request.data["store_password"])

            if password_validation_response:
                return password_validation_response

            request.data["store_password"] = make_password(
                request.data["store_password"])

            if Store.objects.filter(store_email=request.data['store_email'], is_deleted=False).exists():
                return CustomBadRequest(message=USER_ALREADY_EXISTS)

            registration_serializer = StoreRegistrationSerializer(
                data=request.data)

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


class EmployeeManagement(APIView):
    authentication_classes = [StoreJWTAuthentication]

    @staticmethod
    def patch(request):
        try:
            employee_id = request.data.get("employee_id")

            if not employee_id:
                return CustomBadRequest(message=BAD_REQUEST)

            if Employee.objects.filter(employee_id=employee_id, is_deleted=False).exists() is False:
                return CustomNotFound(message=DATA_NOT_FOUND)

            employee = Employee.objects.get(
                employee_id=employee_id,
                is_deleted=False
            )

            if "employee_email" in request.data:
                if (Employee.objects.filter(employee_email=request.data["employee_email"],
                                            is_deleted=False).exists() and
                        employee.employee_email != request.data["employee_email"]):

                    return CustomBadRequest(message=USER_ALREADY_EXISTS)

                email_validation = validate_email(
                    request.data['employee_email'])

            if "employee_password" in request.data:
                password_validation_response = validate_password(
                    request.data["employee_password"])

                if password_validation_response:
                    return password_validation_response

                request.data["employee_password"] = make_password(
                    request.data["employee_password"])

            employee_details_management_serializer = EmployeeDetailsManagementSerializer(
                employee,
                data=request.data,
                partial=True
            )

            if employee_details_management_serializer.is_valid():
                employee_details_management_serializer.save()

                update_store_services(
                    employee_details_management_serializer.data)
                updpate_store_langauges(
                    employee_details_management_serializer.data)

                return GenericSuccessResponse(
                    employee_details_management_serializer.data,
                    message="Employee details updated successfully",
                    status=200
                )

            return CustomBadRequest(message=employee_details_management_serializer.errors)

        except Exception:
            return GenericException(request=request)

    @staticmethod
    def post(request):
        try:
            if (
                not request.data.get("employee_email") or
                not request.data.get("employee_name")
            ):
                return CustomBadRequest(message=BAD_REQUEST)

            if Employee.objects.filter(employee_email=request.data['employee_email'], is_deleted=False).exists():
                return CustomBadRequest(message=USER_ALREADY_EXISTS)

            store = request.user

            request.data["store_id"] = store.store_id

            raw_string = f"{request.data['employee_name']}{request.data['employee_email']}".lower(
            )
            password = hashlib.md5(raw_string.encode()).hexdigest()[:8]

            request.data["employee_password"] = make_password(password)

            employee_registration_serializer = EmployeeRegistrationSerializer(
                data=request.data)

            if employee_registration_serializer.is_valid():

                # Uncomment the lines below to send an email with the generated password to the employee

                # message = f"Hi {request.data['employee_name']},\n\nYour password is: {password}\n\nBest Regards,\n{store.store_name}"

                # send_registration_email(
                #     request.data['employee_email'],
                #     request.data['employee_name'],
                #     message=message
                # )

                employee_registration_serializer.save()

                return GenericSuccessResponse(
                    message=f"Registration successful. Password: {password}",
                    status=201
                )

            return CustomBadRequest(message=employee_registration_serializer.errors)

        except Exception:
            return GenericException(request=request)

    @staticmethod
    def get(request):
        try:
            employee_id = request.query_params.get("employee_id")

            if not employee_id:
                return CustomBadRequest(message=BAD_REQUEST)

            employees = Employee.objects.filter(
                employee_id=employee_id,
                is_deleted=False
            )

            fetch_employee_details_serializer = FetchEmployeeDetailsSerializer(
                employees,
                many=True
            )

            return GenericSuccessResponse(
                fetch_employee_details_serializer.data,
                message="Fetched employees data successfully",
                status=200
            )

        except Exception:
            return GenericException(request=request)

    @staticmethod
    def delete(request):
        try:
            employee_id = request.query_params.get("employee_id")

            employee = Employee.objects.get(employee_id=employee_id)

            employee.is_deleted = True
            employee.save()

            return GenericSuccessResponse(message="Employee deleted successfully", status=200)

        except Employee.DoesNotExist:
            return CustomBadRequest(message=USER_DOES_NOT_EXIST)

        except Exception:
            return GenericException(request=request)


class FetchEmployeesList(APIView):
    authentication_classes = [StoreJWTAuthentication]

    @staticmethod
    def get(request):
        try:
            store = request.user
            employees = Employee.objects.filter(
                store_id=store.store_id, is_deleted=False)
            employee_registration_serializer = EmployeeRegistrationSerializer(
                employees, many=True)
            return GenericSuccessResponse(employee_registration_serializer.data,
                                          message="Fetched employees data successfully",
                                          status=200)

        except Exception:
            return GenericException(request=request)


class StoreDetailsManagement(APIView):
    authentication_classes = [StoreJWTAuthentication]

    @staticmethod
    def get(request):
        try:
            store = request.user
            store_details_management_serializer = StoreDetailsManagementSerializer(
                store)
            return GenericSuccessResponse(store_details_management_serializer.data,
                                          message=FETCHED_STORE_DATA_SUCCESFULLY,
                                          status=200)

        except Exception:
            return GenericException(request=request)

    @staticmethod
    def patch(request):
        try:
            store = request.user

            if (
                "store_email" not in request.data or
                "store_address" not in request.data or
                "store_name" not in request.data or
                "store_contact_number" not in request.data or
                "store_password" not in request.data
            ):
                return CustomBadRequest(message=BAD_REQUEST)

            email_validation = validate_email(request.data['store_email'])

            if (Store.objects.filter(store_email=request.data['store_email'],
                                     is_deleted=False).exists() and
                    store.store_email != request.data['store_email']):
                return CustomBadRequest(message=EMAIL_IS_NOT_AVAILABLE)

            password_validation_response = validate_password(
                request.data["store_password"])

            if password_validation_response:
                return password_validation_response

            request.data["store_password"] = make_password(
                request.data["store_password"])

            store_details_management_serializer = StoreDetailsManagementSerializer(
                store, data=request.data, partial=True)

            if store_details_management_serializer.is_valid():
                store_details_management_serializer.save()

                return GenericSuccessResponse(store_details_management_serializer.data,
                                              message=STORE_DETAILS_UPDATED_SUCCESSFULLY,
                                              status=200)

            return CustomBadRequest(message=store_details_management_serializer.errors)

        except EmailNotValidError as e:
            return CustomBadRequest(message=str(e))

        except Exception:
            return GenericException(request=request)
