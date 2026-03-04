from store.models import Store
from enum import Enum
from django.db import models

from common.models import Audit


class Employee(Audit):
    class Meta:
        db_table = 'cx_employee'

    employee_id = models.BigAutoField(primary_key=True)
    store_id = models.ForeignKey(
        Store, on_delete=models.CASCADE, null=True, blank=True)
    employee_name = models.CharField(max_length=255, null=True, blank=True)
    employee_email = models.EmailField(null=True, blank=True)
    employee_password = models.CharField(max_length=255, null=True, blank=True)
    employee_address = models.TextField(null=True, blank=True)
    employee_contact_number = models.CharField(
        max_length=15, null=True, blank=True)
    employee_langauges = models.JSONField(
        max_length=255, null=True, blank=True)
    employee_skills = models.JSONField(max_length=255, null=True, blank=True)
    employee_charges = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
