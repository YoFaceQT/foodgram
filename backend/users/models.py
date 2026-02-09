from django.contrib.auth.models import AbstractUser
from django.db import models


NAME_MAX_LENGHT = 150


class User(AbstractUser):
    """Модель User"""

    email = models.EmailField(
        'Электронная почта',
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
