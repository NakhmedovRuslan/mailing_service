from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ["email", "username", "avatar", "is_active"]
    list_filter = ["email", "username", "is_active"]
    search_fields = ["email", "username"]
    ordering = ["email"]

    readonly_fields = ("date_joined", "last_login")
