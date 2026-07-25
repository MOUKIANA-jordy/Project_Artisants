from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from rest_framework import (
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.notifications.models import Notification
from apps.notifications.services import create_notification

from apps.core.pagination import StandardResultsSetPagination

from .models import Conversation, Message
from .permissions import (
    IsConversationParticipant,
    IsMessageParticipant,
)
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
)


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsConversationParticipant,
    ]

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = (
            Conversation.objects
            .select_related(
                "client",
                "artisan",
                "artisan__user",
                "demande",
            )
            .prefetch_related(
                "artisan__categories",
                "messages",
            )
        )

        user = self.request.user

        if user.is_staff:
            return queryset

        return queryset.filter(
            Q(client=user)
            | Q(artisan__user=user)
        ).distinct()

    @action(
        detail=True,
        methods=["post"],
        url_path="marquer-lus",
    )
    def marquer_lus(self, request, pk=None):
        conversation = self.get_object()

        messages = conversation.messages.filter(
            is_read=False,
        ).exclude(
            sender=request.user,
        )

        messages.update(
            is_read=True,
            read_at=timezone.now(),
        )

        return Response(
            {
                "detail": "Les messages ont été marqués comme lus."
            },
            status=status.HTTP_200_OK,
        )


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsMessageParticipant,
    ]

    pagination_class = StandardResultsSetPagination

    http_method_names = [
        "get",
        "post",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        queryset = (
            Message.objects
            .select_related(
                "sender",
                "conversation",
                "conversation__client",
                "conversation__artisan",
                "conversation__artisan__user",
            )
        )

        conversation_id = self.kwargs.get(
            "conversation_pk"
        )

        queryset = queryset.filter(
            conversation_id=conversation_id
        )

        user = self.request.user

        if user.is_staff:
            return queryset

        return queryset.filter(
            Q(conversation__client=user)
            | Q(conversation__artisan__user=user)
        )

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get(
            "conversation_pk"
        )

        try:
            conversation = Conversation.objects.select_related(
                "client",
                "artisan__user",
            ).get(
                pk=conversation_id
            )
        except Conversation.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "detail": "Cette conversation n’existe pas."
                }
            )

        user = self.request.user

        is_participant = (
            conversation.client == user
            or conversation.artisan.user == user
            or user.is_staff
        )

        if not is_participant:
            raise permissions.PermissionDenied(
                "Vous ne participez pas à cette conversation."
            )

        if not conversation.is_active:
            raise serializers.ValidationError(
                {
                    "detail": "Cette conversation est fermée."
                }
            )

        message = serializer.save(
        conversation=conversation,
        sender=user,
)
        if conversation.client == user:
    destinataire = conversation.artisan.user
else:
    destinataire = conversation.client

create_notification(
    destinataire=destinataire,
    type_notification=Notification.Type.NOUVEAU_MESSAGE,
    titre="Nouveau message",
    message=f"Nouveau message de {user.get_full_name() or user.email}.",
    lien=f"/conversations/{conversation.id}",
)

        conversation.save(
            update_fields=["updated_at"]
        )

    def perform_destroy(self, instance):
        if (
            instance.sender != self.request.user
            and not self.request.user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Vous ne pouvez supprimer que vos propres messages."
            )

        instance.delete()
