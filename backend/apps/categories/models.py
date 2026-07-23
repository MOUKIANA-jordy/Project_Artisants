from django.db import models

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    nom = models.CharField(
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
    )
    description = models.TextField(
        blank=True,
    )
    icone = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nom d'une icône ou classe CSS",
    )
    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "categories"
        ordering = ["nom"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom
