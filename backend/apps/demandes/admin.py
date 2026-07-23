from django.contrib import admin
from .models import DemandeImage, DemandeTravaux


@admin.register(DemandeTravaux)
class DemandeTravauxAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titre",
        "client",
        "categorie",
        "ville",
        "statut",
        "is_urgent",
        "created_at",
    )

    list_filter = (
        "statut",
        "is_urgent",
        "ville",
        "categorie",
    )

    search_fields = (
        "titre",
        "description",
        "client__email",
    )


@admin.register(DemandeImage)
class DemandeImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "demande",
        "legende",
        "ordre",
        "created_at",
    )

    search_fields = (
        "demande__titre",
        "legende",
    )
