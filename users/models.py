from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField("Имя", max_length=100, null=False, blank=False)
    last_name = models.CharField("Фамилия", max_length=100, null=False, blank=False)
    username = models.CharField("Никнейм", max_length=100, null=False, blank=False)
    avatar = models.ImageField("Аватар", upload_to="avatars/", null=True, blank=True)
    is_active = models.BooleanField("Подтвержденный пользователь", default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    token = models.CharField(
        max_length=100, verbose_name="Токен", blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_users", "Может просматривать список пользователей"),
            ("can_block_users", "Может блокировать пользователей"),
        ]
