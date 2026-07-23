from django.conf import settings
from django.db import models

from apps.categories.models import Category
from apps.core.models import TimeStampedModel


class Artisan(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artisan_profile",
    )

    nom_entreprise = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    categories = models.ManyToManyField(
        Category,
        related_name="artisans",
        blank=True,
    )

    ville = models.CharField(
        max_length=100,
    )

    quartier = models.CharField(
        max_length=100,
        blank=True,
    )

    adresse = models.TextField(
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
    )

    experience = models.PositiveIntegerField(
        default=0,
        help_text="Nombre d'années d'expérience",
    )

    verified = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "artisans"
        ordering = ["-created_at"]
        verbose_name = "Artisan"
        verbose_name_plural = "Artisans"

    def __str__(self):
        return self.nom_entreprise


class ArtisanImage(TimeStampedModel):
    artisan = models.ForeignKey(
        Artisan,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="artisans/realisations/",
    )

    legende = models.CharField(
        max_length=200,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
        help_text="Image principale du profil artisan",
    )

    ordre = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        db_table = "artisan_images"
        ordering = [
            "-is_primary",
            "ordre",
            "-created_at",
        ]
        verbose_name = "Image artisan"
        verbose_name_plural = "Images artisans"

    def __str__(self):
        return (
            f"Image de {self.artisan.nom_entreprise}"
        )

    def save(self, *args, **kwargs):
        if self.is_primary:
            ArtisanImage.objects.filter(
                artisan=self.artisan,
                is_primary=True,
            ).exclude(
                pk=self.pk,
            ).update(
                is_primary=False
            )

        super().save(*args, **kwargs)
