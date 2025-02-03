from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, verbose_name="username", help_text="Введите имя пользователя")
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Введите свой email")
    phone_number = models.CharField(
        max_length=15,
        verbose_name="Телефон",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    avatar = models.ImageField(
        upload_to="photo/avatar",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Страна",
        help_text="Укажите страну",
    )
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]
        permissions = [
            ("can_manage_users", "can manage users"),
            ("can_block_users", "can block users"),
        ]

    def __str__(self):
        return self.email
