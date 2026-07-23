from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.artisans.models import Artisan
from apps.core.models import TimeStampedModel
from apps.demandes.models import DemandeTravaux


class Review(TimeStampedModel):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )

    artisan = models.ForeignKey(
        Artisan,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    demande = models.OneToOneField(
        DemandeTravaux,
        on_delete=models.CASCADE,
        related_name="review",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    commentaire = models.TextField(
        blank=True,
    )

    is_visible = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "artisan", "demande"],
                name="unique_review_per_completed_job",
            )
        ]

    def __str__(self):
        return (
            f"{self.client.email} - "
            f"{self.artisan.nom_entreprise} - "
            f"{self.rating}/5"
        )
