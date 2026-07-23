from django.conf import settings
from django.db import models

from apps.categories.models import Category
from apps.core.models import TimeStampedModel


class DemandeTravaux(TimeStampedModel):
    class Statut(models.TextChoices):
        BROUILLON = "brouillon", "Brouillon"
        PUBLIEE = "publiee", "Publiée"
        EN_COURS = "en_cours", "En cours"
        TERMINEE = "terminee", "Terminée"
        ANNULEE = "annulee", "Annulée"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demandes_travaux",
    )

    categorie = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="demandes_travaux",
    )

    titre = models.CharField(
        max_length=150,
    )

    description = models.TextField()

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

    budget_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    budget_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    date_souhaitee = models.DateField(
        null=True,
        blank=True,
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
    )

    is_urgent = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "demandes_travaux"
        ordering = ["-created_at"]
        verbose_name = "Demande de travaux"
        verbose_name_plural = "Demandes de travaux"

    def __str__(self):
        return self.titre

class DemandeImage(TimeStampedModel):
    demande = models.ForeignKey(
        DemandeTravaux,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="demandes/photos/",
    )

    legende = models.CharField(
        max_length=200,
        blank=True,
    )

    ordre = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        db_table = "demande_images"
        ordering = [
            "ordre",
            "created_at",
        ]
        verbose_name = "Image de demande"
        verbose_name_plural = "Images de demandes"

    def __str__(self):
        return f"Image de la demande {self.demande_id}"
