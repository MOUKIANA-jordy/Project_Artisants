from rest_framework import permissions, viewsets
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

        return queryset.filter(
            artisan_id=artisan_id
        )

    def perform_create(self, serializer):
        artisan = self.request.user.artisan_profile

        if str(artisan.id) != str(
            self.kwargs.get("artisan_pk")
        ):
            raise permissions.PermissionDenied(
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
            raise permissions.PermissionDenied(
                "Vous ne pouvez pas modifier cette image."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if (
            instance.artisan.user != self.request.user
            and not self.request.user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Vous ne pouvez pas supprimer cette image."
            )

        instance.delete()
