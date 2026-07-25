from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from apps.artisans.serializers import ArtisanSerializer

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "sender",
            "contenu",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "conversation",
            "sender",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        )

    def validate_contenu(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Le message ne peut pas être vide."
            )

        if len(value) > 5000:
            raise serializers.ValidationError(
                "Le message ne peut pas dépasser 5000 caractères."
            )

        return value


class ConversationSerializer(serializers.ModelSerializer):
    client = UserPublicSerializer(read_only=True)
    artisan = ArtisanSerializer(read_only=True)

    demande_titre = serializers.CharField(
        source="demande.titre",
        read_only=True,
    )

    dernier_message = serializers.SerializerMethodField()
    messages_non_lus = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "id",
            "demande",
            "demande_titre",
            "client",
            "artisan",
            "is_active",
            "dernier_message",
            "messages_non_lus",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_dernier_message(self, obj):
        message = obj.messages.order_by(
            "-created_at"
        ).first()

        if message is None:
            return None

        return {
            "id": message.id,
            "contenu": message.contenu,
            "sender_id": message.sender_id,
            "is_read": message.is_read,
            "created_at": message.created_at,
        }

    def get_messages_non_lus(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return 0

        return obj.messages.filter(
            is_read=False,
        ).exclude(
            sender=request.user,
        ).count()
