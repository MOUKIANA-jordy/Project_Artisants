from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser

from .models import DemandeImage, DemandeTravaux
from .serializers_images import DemandeImageSerializer


class DemandeImageViewSet(viewsets.ModelViewSet):
    serializer_class = DemandeImageSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):
        queryset = DemandeImage.objects.select_related(
            "demande",
            "demande__client",
        )

        demande_id = self.kwargs.get("demande_pk")

        queryset = queryset.filter(
            demande_id=demande_id
        )

        user = self.request.user

        # L'administrateur peut voir toutes les images.
        if user.is_authenticated and user.is_staff:
            return queryset

        statuts_publics = [
            DemandeTravaux.Statut.PUBLIEE,
            DemandeTravaux.Statut.EN_COURS,
        ]

        # Un utilisateur connecté peut voir :
        # - les images des demandes publiques ;
        # - les images de ses propres demandes.
        if user.is_authenticated:
            return queryset.filter(
                Q(
                    demande__statut__in=statuts_publics
                )
                | Q(
                    demande__client=user
                )
            )

        # Un visiteur anonyme ne voit que les images
        # des demandes publiques.
        return queryset.filter(
            demande__statut__in=statuts_publics
        )

    def perform_create(self, serializer):
        demande = DemandeTravaux.objects.get(
            pk=self.kwargs.get("demande_pk")
        )

        if (
            demande.client != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas ajouter d’image "
                "à cette demande."
            )

        serializer.save(
            demande=demande
        )

    def perform_update(self, serializer):
        image = self.get_object()

        if (
            image.demande.client != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas modifier cette image."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if (
            instance.demande.client != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas supprimer cette image."
            )

        instance.delete()
