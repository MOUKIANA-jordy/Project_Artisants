from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser

from .models import ArtisanImage
from .serializers_images import ArtisanImageSerializer


class ArtisanImageViewSet(viewsets.ModelViewSet):
    serializer_class = ArtisanImageSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):
        queryset = ArtisanImage.objects.select_related(
            "artisan",
            "artisan__user",
        )

        artisan_id = self.kwargs.get("artisan_pk")

        queryset = queryset.filter(
            artisan_id=artisan_id
        )

        user = self.request.user

        # L'administrateur peut voir les images
        # des profils actifs et inactifs.
        if user.is_authenticated and user.is_staff:
            return queryset

        # Le public et les utilisateurs normaux
        # ne voient que les images des artisans actifs.
        return queryset.filter(
            artisan__is_active=True
        )

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "artisan_profile"):
            raise PermissionDenied(
                "Vous devez avoir un profil artisan "
                "pour ajouter une image."
            )

        artisan = user.artisan_profile

        if str(artisan.id) != str(
            self.kwargs.get("artisan_pk")
        ):
            raise PermissionDenied(
                "Vous ne pouvez ajouter des images "
                "qu’à votre propre profil."
            )

        serializer.save(
            artisan=artisan
        )

    def perform_update(self, serializer):
        image = self.get_object()

        if (
            image.artisan.user != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas modifier cette image."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if (
            instance.artisan.user != self.request.user
            and not self.request.user.is_staff
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas supprimer cette image."
            )

        instance.delete()
