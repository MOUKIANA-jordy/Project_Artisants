from rest_framework import permissions, viewsets
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

        return queryset.filter(
            demande_id=demande_id
        )

    def perform_create(self, serializer):
        demande = DemandeTravaux.objects.get(
            pk=self.kwargs.get("demande_pk")
        )

        if (
            demande.client != self.request.user
            and not self.request.user.is_staff
        ):
            raise permissions.PermissionDenied(
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
            raise permissions.PermissionDenied(
                "Vous ne pouvez pas modifier cette image."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if (
            instance.demande.client != self.request.user
            and not self.request.user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Vous ne pouvez pas supprimer cette image."
            )

        instance.delete()
