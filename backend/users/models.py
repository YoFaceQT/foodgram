from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import username_validator


NAME_MAX_LENGHT = 150
EMAIL_MAX_LENGHT = 254


class User(AbstractUser):
    """Модель User"""

    username = models.CharField(
        'Пользователь',
        max_length=NAME_MAX_LENGHT,
        unique=True,
        validators=[username_validator]
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_MAX_LENGHT,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_MAX_LENGHT
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_MAX_LENGHT
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
