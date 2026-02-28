
import datetime
import jwt


from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from django.core.exceptions import PermissionDenied
from django.db.models import Q


from codeX import settings

from common.constants import SERIALIZER_IS_NOT_VALID, TOKEN_IS_EXPIRED, USER_NOT_FOUND

from store.models import Store

from exceptions.generic import CustomBadRequest, GenericException

from security.serializers import StoreAuthTokenSerializer
from security.models import StoreAuthTokens


def get_store_authentication_token(store):
    store_refresh_token = jwt.encode(
        payload={
            "token_type": "refresh",
            "store_id": store.store_id,
            "email": store.store_email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + settings.REFRESH_TOKEN_LIFETIME
        },
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    store_access_token = jwt.encode(
        payload={
            "token_type": "access",
            "store_id": store.store_id,
            "email": store.store_email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + settings.ACCESS_TOKEN_LIFETIME
        },
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return {
        "store_access_token": store_access_token,
        "store_refresh_token": store_refresh_token
    }


def save_token(token):
    store_auth_token_serializer = StoreAuthTokenSerializer(
        data={
            "access_token": token["store_access_token"],
            "refresh_token": token["store_refresh_token"]
        }
    )

    if store_auth_token_serializer.is_valid():
        store_auth_token_serializer.save()
    else:
        raise CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)


class StoreJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            header = request.headers.get("authorization")

            # if "authorization" not in request.headers:
            #     raise PermissionDenied()

            if not header or len(header) < 12:
                return None

            store_token = header.split(" ")[1]

            if not StoreAuthTokens.objects.filter(
                    Q(access_token=store_token) | Q(
                        refresh_token=store_token)
            ).exists():
                raise AuthenticationFailed(detail=TOKEN_IS_EXPIRED)

            claims = jwt.decode(store_token, key=settings.JWT_SECRET, algorithms=[
                                settings.JWT_ALGORITHM])

            store = Store.objects.get(
                store_id=claims["store_id"],
                store_email=claims["email"],
                is_deleted=False
            )

            return store, claims

        # except PermissionDenied as e:
        #     raise PermissionDenied()

        except AuthenticationFailed as e:
            raise AuthenticationFailed(detail=TOKEN_IS_EXPIRED)

        except Store.DoesNotExist:
            return GenericException(message=USER_NOT_FOUND)

        except Exception:
            return GenericException()
