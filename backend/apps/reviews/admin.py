from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "artisan",
        "demande",
        "rating",
        "is_visible",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_visible",
        "created_at",
    )

    search_fields = (
        "client__email",
        "artisan__nom_entreprise",
        "commentaire",
        "demande__titre",
    )

    ordering = (
        "-created_at",
    )
