from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom",
        "slug",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "created_at",
    )
    search_fields = (
        "nom",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("nom",),
    }
    ordering = ("nom",)
