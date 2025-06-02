from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_inn(value):
    if len(value) not in (10, 12):
        raise ValidationError(_("ИНН должен быть длиной 10 или 12 символов"))
    if not value.isdigit():
        raise ValidationError(_("ИНН должен содержать только цифры"))
