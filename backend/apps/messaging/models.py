from django.db import models
from django.conf import settings

from apps.artisans.models import Artisan
from apps.core.models import TimeStampedModel
from apps.demandes.models import DemandeTravaux


class Conversation(TimeStampedModel):
    demande = models.OneToOneField(
        DemandeTravaux,
        on_delete=models.CASCADE,
        related_name="conversation",
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_conversations",
    )

    artisan = models.ForeignKey(
        Artisan,
        on_delete=models.CASCADE,
        related_name="conversations",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return (
            f"{self.client.email} - "
            f"{self.artisan.nom_entreprise}"
        )


class Message(TimeStampedModel):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )

    contenu = models.TextField()

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message de {self.sender.email}"
