from django.db import models

from common.models import Audit


class StoreAuthTokens(Audit):
    class Meta:
        db_table = 'cx_store_auth_tokens'

    access_token = models.TextField(null=True, db_column="auth_access_token")
    refresh_token = models.TextField(null=True, db_column="auth_refresh_token")
