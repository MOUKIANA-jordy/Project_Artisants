from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.core.pagination import StandardResultsSetPagination
from apps.notifications.models import Notification
from apps.notifications.services import create_notification

from .models import Review
from .permissions import IsReviewOwnerOrReadOnly
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsReviewOwnerOrReadOnly,
    ]

    pagination_class = StandardResultsSetPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "artisan",
        "rating",
        "is_visible",
    ]

    search_fields = [
        "commentaire",
        "artisan__nom_entreprise",
        "client__first_name",
        "client__last_name",
    ]

    ordering_fields = [
        "rating",
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        queryset = (
            Review.objects
            .select_related(
                "client",
                "artisan",
                "artisan__user",
                "demande",
            )
            .prefetch_related(
                "artisan__categories",
            )
        )

        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return queryset

        return queryset.filter(
            is_visible=True
        )

    def perform_create(self, serializer):
        artisan = serializer.validated_data.pop("artisan")

        review = serializer.save(
            client=self.request.user,
            artisan=artisan,
        )

        create_notification(
            destinataire=artisan.user,
            type_notification=Notification.Type.NOUVEL_AVIS,
            titre="Nouvel avis reçu",
            message=(
                f"Vous avez reçu une note de "
                f"{review.rating}/5."
            ),
            lien=f"/artisans/{artisan.id}/avis",
        )

    def perform_update(self, serializer):
        review = self.get_object()

        if (
            review.client != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas modifier cet avis."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if (
            instance.client != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas supprimer cet avis."
            )

        instance.is_visible = False
        instance.save(
            update_fields=[
                "is_visible",
                "updated_at",
            ]
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="mes-avis",
        permission_classes=[permissions.IsAuthenticated],
    )
    def mes_avis(self, request):
        queryset = self.get_queryset().filter(
            client=request.user
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )

            return self.get_paginated_response(
                serializer.data
            )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="statistiques",
    )
    def statistiques(self, request):
        artisan_id = request.query_params.get("artisan")

        if not artisan_id:
            return Response(
                {
                    "detail": (
                        "Le paramètre artisan est obligatoire."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(
            artisan_id=artisan_id
        )

        statistiques = queryset.aggregate(
            note_moyenne=Avg("rating")
        )

        note_moyenne = statistiques["note_moyenne"]

        return Response(
            {
                "artisan_id": int(artisan_id),
                "note_moyenne": (
                    round(note_moyenne, 2)
                    if note_moyenne is not None
                    else None
                ),
                "nombre_avis": queryset.count(),
            }
        )
