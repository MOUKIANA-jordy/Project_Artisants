from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "telephone",
        "role",
        "is_verified",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "telephone",
    )

    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Informations supplémentaires",
            {
                "fields": (
                    "telephone",
                    "role",
                    "is_verified",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informations supplémentaires",
            {
                "fields": (
                    "email",
                    "telephone",
                    "role",
                    "is_verified",
                )
            },
        ),
    )
