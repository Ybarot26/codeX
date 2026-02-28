import re

from django.core.mail import send_mail
from django.conf import settings

from common.constants import (PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20,
                              PASSWORD_MUST_HAVE_ONE_NUMBER,
                              PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER,
                              PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER,
                              PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER)

from exceptions.generic import CustomBadRequest


def send_registration_email(email, name, message):
    subject = "Welcome to Our Platform!"
    message = message
    print(email, name)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def validate_password(password):

    special_characters = r"[\$#@!\*]"

    if len(password) < 8 or len(password) > 20:
        return CustomBadRequest(message=PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20)
    if re.search('[0-9]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_NUMBER)
    if re.search('[a-z]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER)
    if re.search('[A-Z]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER)
    if re.search(special_characters, password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER)
