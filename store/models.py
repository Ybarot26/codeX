from enum import Enum
from django.db import models

from common.models import Audit


class Store(Audit):
    class Meta:
        db_table = 'cx_store'

    store_id = models.BigAutoField(primary_key=True)
    store_name = models.CharField(max_length=255, null=True, blank=True)
    store_email = models.EmailField(null=True, blank=True)
    store_password = models.CharField(max_length=255, null=True, blank=True)
    store_address = models.TextField(null=True, blank=True)
    store_contact_number = models.CharField(
        max_length=15, null=True, blank=True)
