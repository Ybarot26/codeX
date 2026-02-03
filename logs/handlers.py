import logging
import traceback

from exceptions.generic import GenericException


class DBHandler(logging.Handler):
    def emit(self, record):
        try:

            if record.status_code == 500:
                if record.request_method and record.request_url:

                    from logs.models import LogEntry

                    request_method = record.request_method
                    request_url = record.request_url

                    traceback_str = ""

                    if record.exc_info:
                        traceback_str = ''.join(
                            traceback.format_exception(
                                record.exc_info[0],
                                record.exc_info[1],
                                record.exc_info[2]
                            ))

                    LogEntry.objects.create(
                        traceback=traceback_str,
                        request_method=request_method,
                        request_url=request_url,
                    )

        except Exception:
            GenericException()
