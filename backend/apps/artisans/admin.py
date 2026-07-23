from django.contrib import admin
from .models import Artisan, ArtisanImage


@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom_entreprise",
        "user",
        "ville",
        "quartier",
        "experience",
        "verified",
        "is_active",
    )

    list_filter = (
        "verified",
        "is_active",
        "ville",
        "categories",
    )

    search_fields = (
        "nom_entreprise",
        "user_email",
        "user_username",
        "ville",
        "quartier",
    )

    filter_horizontal = (
        "categories",
    )

@admin.register(ArtisanImage)
class ArtisanImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "artisan",
        "legende",
        "is_primary",
        "ordre",
        "created_at",
    )

    list_filter = (
        "is_primary",
        "created_at",
    )

    search_fields = (
        "artisan__nom_entreprise",
        "legende",
    )
