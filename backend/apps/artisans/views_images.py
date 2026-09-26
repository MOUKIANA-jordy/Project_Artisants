from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import ArtisanImage
from .serializers_images import ArtisanImageSerializer


class ArtisanImageViewSet(viewsets.ModelViewSet):
    serializer_class = ArtisanImageSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
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

        if user.is_authenticated and user.is_staff:
            return queryset

        return queryset.filter(
            artisan__is_active=True
        )

    def create(self, request, *args, **kwargs):
        user = request.user

        # Seul un utilisateur possédant un profil artisan
        # peut ajouter une image.
        if not hasattr(user, "artisan_profile"):
            raise PermissionDenied(
                "Seul un artisan peut ajouter une image."
            )

        artisan = user.artisan_profile
        artisan_id = self.kwargs.get("artisan_pk")

        # Un artisan ne peut ajouter une image
        # qu'à son propre profil.
        if str(artisan.id) != str(artisan_id):
            raise PermissionDenied(
                "Vous ne pouvez ajouter des images "
                "qu'à votre propre profil artisan."
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            artisan=artisan
        )

        headers = self.get_success_headers(
            serializer.data
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
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
