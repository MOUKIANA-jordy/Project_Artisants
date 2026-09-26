from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.core.pagination import StandardResultsSetPagination

from .filters import DemandeTravauxFilter
from .models import DemandeTravaux
from .permissions import IsDemandOwnerOrReadOnly
from .serializers import DemandeTravauxSerializer


class DemandeTravauxViewSet(viewsets.ModelViewSet):
    serializer_class = DemandeTravauxSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsDemandOwnerOrReadOnly,
    ]

    pagination_class = StandardResultsSetPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = DemandeTravauxFilter

    search_fields = [
        "titre",
        "description",
        "ville",
        "quartier",
        "categorie__nom",
    ]

    ordering_fields = [
        "created_at",
        "date_souhaitee",
        "budget_min",
        "budget_max",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            DemandeTravaux.objects
            .select_related("client", "categorie")
            .prefetch_related("propositions")
            .distinct()
        )

        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return queryset

        statuts_publics = [
            DemandeTravaux.Statut.PUBLIEE,
            DemandeTravaux.Statut.EN_COURS,
        ]

        if user.is_authenticated:
            return queryset.filter(
                Q(statut__in=statuts_publics)
                | Q(client=user)
            )

        return queryset.filter(
            statut__in=statuts_publics
        )

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "client":
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Seul un client peut créer une demande "
                        "de travaux."
                    )
                }
            )

        serializer.save(
            client=user,
            statut=DemandeTravaux.Statut.BROUILLON,
        )

    def perform_update(self, serializer):
        demande = self.get_object()

        if demande.statut in (
            DemandeTravaux.Statut.TERMINEE,
            DemandeTravaux.Statut.ANNULEE,
        ):
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Une demande terminée ou annulée "
                        "ne peut plus être modifiée."
                    )
                }
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.statut == DemandeTravaux.Statut.TERMINEE:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Une demande terminée ne peut pas être supprimée."
                    )
                }
            )

        instance.statut = DemandeTravaux.Statut.ANNULEE
        instance.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="mes-demandes",
        permission_classes=[permissions.IsAuthenticated],
    )
    def mes_demandes(self, request):
        queryset = self.get_queryset().filter(
            client=request.user
        )

        queryset = self.filter_queryset(queryset)

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
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def publier(self, request, pk=None):
        demande = self.get_object()

        if (
            demande.client != request.user
            and not request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas publier cette demande."
            )

        if demande.statut != DemandeTravaux.Statut.BROUILLON:
            return Response(
                {
                    "detail": (
                        "Seule une demande en brouillon "
                        "peut être publiée."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        demande.statut = DemandeTravaux.Statut.PUBLIEE
        demande.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(demande)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def annuler(self, request, pk=None):
        demande = self.get_object()

        if (
            demande.client != request.user
            and not request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas annuler cette demande."
            )

        if demande.statut in (
            DemandeTravaux.Statut.TERMINEE,
            DemandeTravaux.Statut.ANNULEE,
        ):
            return Response(
                {
                    "detail": (
                        "Cette demande est déjà terminée ou annulée."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        demande.statut = DemandeTravaux.Statut.ANNULEE
        demande.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "La demande a été annulée."
            },
            status=status.HTTP_200_OK,
        )
     
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def terminer(self, request, pk=None):
        demande = self.get_object()

        if (
            demande.client != request.user
            and not request.user.is_staff
        ):
            raise PermissionDenied(
                "Seul le client peut terminer cette demande."
            )

        if demande.statut != DemandeTravaux.Statut.EN_COURS:
            return Response(
                {
                    "detail": (
                        "Seule une demande en cours "
                        "peut être terminée."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not demande.propositions.filter(
            statut="acceptee"
        ).exists():
            return Response(
                {
                    "detail": (
                        "Aucune proposition acceptée "
                        "n'est liée à cette demande."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        demande.statut = DemandeTravaux.Statut.TERMINEE
        demande.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(demande)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
