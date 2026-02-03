from django.db import models

from common.models import Audit


class LogEntry(Audit):
    class Meta:
        db_table = 'cx_logs'

    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    request_method = models.CharField(max_length=10, null=True, blank=True)

    traceback = models.TextField(blank=True, null=True)

    request_url = models.URLField(null=True, blank=True)
