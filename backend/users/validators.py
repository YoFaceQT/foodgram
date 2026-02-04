import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def username_validator(value):
    """Валидатор имени пользователя."""

    if len(value) > 150:
        raise ValidationError(
            _('Имя пользователя не должно превышать 150 символов.'),
            params={'value': value},
        )

    pattern = r'^[\w.@+-]+\Z'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Имя пользователя содержит запрещенные символы'),
            params={'value': value},
        )
