from django.db import models

from apps.artisans.models import Artisan
from apps.core.models import TimeStampedModel
from apps.demandes.models import DemandeTravaux


class Proposition(TimeStampedModel):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        ACCEPTEE = "acceptee", "Acceptée"
        REFUSEE = "refusee", "Refusée"
        RETIREE = "retiree", "Retirée"

    demande = models.ForeignKey(
        DemandeTravaux,
        on_delete=models.CASCADE,
        related_name="propositions",
    )

    artisan = models.ForeignKey(
        Artisan,
        on_delete=models.CASCADE,
        related_name="propositions",
    )

    message = models.TextField()

    prix_propose = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    date_disponibilite = models.DateField(
        null=True,
        blank=True,
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE,
    )

    class Meta:
        db_table = "propositions"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["demande", "artisan"],
                name="unique_proposition_par_artisan",
            )
        ]

    def __str__(self):
        return f"{self.artisan} - {self.demande}"
