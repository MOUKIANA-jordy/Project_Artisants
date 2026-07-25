from django.shortcuts import render
from django.utils import timezone
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.pagination import StandardResultsSetPagination

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(
            destinataire=self.request.user
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="marquer-lue",
    )
    def marquer_lue(self, request, pk=None):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(
                update_fields=[
                    "is_read",
                    "read_at",
                    "updated_at",
                ]
            )

        return Response(
            self.get_serializer(notification).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="marquer-toutes-lues",
    )
    def marquer_toutes_lues(self, request):
        Notification.objects.filter(
            destinataire=request.user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )

        return Response(
            {
                "detail": (
                    "Toutes les notifications ont été "
                    "marquées comme lues."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="non-lues",
    )
    def non_lues(self, request):
        queryset = self.get_queryset().filter(
            is_read=False
        )

        return Response(
            {
                "count": queryset.count(),
                "results": self.get_serializer(
                    queryset,
                    many=True,
                ).data,
            }
        )
