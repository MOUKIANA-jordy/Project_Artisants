from django.db import models
from django.conf import settings

from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Type(models.TextChoices):
        NOUVELLE_PROPOSITION = (
            "nouvelle_proposition",
            "Nouvelle proposition",
        )
        PROPOSITION_ACCEPTEE = (
            "proposition_acceptee",
            "Proposition acceptée",
        )
        PROPOSITION_REFUSEE = (
            "proposition_refusee",
            "Proposition refusée",
        )
        NOUVEAU_MESSAGE = (
            "nouveau_message",
            "Nouveau message",
        )
        NOUVEL_AVIS = (
            "nouvel_avis",
            "Nouvel avis",
        )
        ARTISAN_VERIFIE = (
            "artisan_verifie",
            "Artisan vérifié",
        )

    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    type = models.CharField(
        max_length=50,
        choices=Type.choices,
    )

    titre = models.CharField(
        max_length=150,
    )

    message = models.TextField()

    lien = models.CharField(
        max_length=255,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.destinataire.email} - {self.titre}"
