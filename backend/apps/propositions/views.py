from django.db import transaction
from rest_framework import (
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.demandes.models import DemandeTravaux

from .models import Proposition
from .permissions import IsPropositionParticipant
from .serializers import PropositionSerializer


class PropositionViewSet(viewsets.ModelViewSet):
    serializer_class = PropositionSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsPropositionParticipant,
    ]

    def get_queryset(self):
        queryset = (
            Proposition.objects
            .select_related(
                "artisan",
                "artisan__user",
                "demande",
                "demande__client",
            )
            .prefetch_related(
                "artisan__categories",
            )
        )

        user = self.request.user

        if user.is_staff:
            return queryset

        if hasattr(user, "artisan_profile"):
            return queryset.filter(
                artisan=user.artisan_profile
            )

        return queryset.filter(
            demande__client=user
        )

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(
            user,
            "artisan_profile",
        ):
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Vous devez avoir un profil artisan."
                    )
                }
            )

        demande = serializer.validated_data["demande"]

        if demande.statut != DemandeTravaux.Statut.PUBLIEE:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Cette demande n'accepte plus "
                        "de propositions."
                    )
                }
            )

        if Proposition.objects.filter(
            demande=demande,
            artisan=user.artisan_profile,
        ).exists():
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Vous avez déjà envoyé une proposition "
                        "pour cette demande."
                    )
                }
            )

        serializer.save(
            artisan=user.artisan_profile
        )

    def perform_update(self, serializer):
        proposition = self.get_object()
        user = self.request.user

        if (
            proposition.artisan.user != user
            and not user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Seul l'artisan peut modifier sa proposition."
            )

        if proposition.statut != Proposition.Statut.EN_ATTENTE:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Cette proposition ne peut plus "
                        "être modifiée."
                    )
                }
            )

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if (
            instance.artisan.user != user
            and not user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Seul l'artisan peut retirer sa proposition."
            )

        if instance.statut != Proposition.Statut.EN_ATTENTE:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Cette proposition ne peut plus "
                        "être retirée."
                    )
                }
            )

        instance.statut = Proposition.Statut.RETIREE
        instance.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="recues",
    )
    def recues(self, request):
        queryset = self.get_queryset().filter(
            demande__client=request.user
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="envoyees",
    )
    def envoyees(self, request):
        if not hasattr(
            request.user,
            "artisan_profile",
        ):
            return Response(
                [],
                status=status.HTTP_200_OK,
            )

        queryset = self.get_queryset().filter(
            artisan=request.user.artisan_profile
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
    )
    @transaction.atomic
    def accepter(self, request, pk=None):
        proposition = self.get_object()

        if (
            proposition.demande.client
            != request.user
            and not request.user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Seul le client peut accepter cette proposition."
            )

        if (
            proposition.statut
            != Proposition.Statut.EN_ATTENTE
        ):
            return Response(
                {
                    "detail": (
                        "Cette proposition n'est plus en attente."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        demande = proposition.demande

        if demande.statut != DemandeTravaux.Statut.PUBLIEE:
            return Response(
                {
                    "detail": (
                        "Cette demande ne peut plus "
                        "accepter de proposition."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        proposition.statut = Proposition.Statut.ACCEPTEE
        proposition.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

        Proposition.objects.filter(
            demande=demande,
            statut=Proposition.Statut.EN_ATTENTE,
        ).exclude(
            pk=proposition.pk
        ).update(
            statut=Proposition.Statut.REFUSEE
        )

        demande.statut = DemandeTravaux.Statut.EN_COURS
        demande.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(proposition)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def refuser(self, request, pk=None):
        proposition = self.get_object()

        if (
            proposition.demande.client
            != request.user
            and not request.user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Seul le client peut refuser cette proposition."
            )

        if (
            proposition.statut
            != Proposition.Statut.EN_ATTENTE
        ):
            return Response(
                {
                    "detail": (
                        "Cette proposition n'est plus en attente."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        proposition.statut = Proposition.Statut.REFUSEE
        proposition.save(
            update_fields=[
                "statut",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(proposition)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
