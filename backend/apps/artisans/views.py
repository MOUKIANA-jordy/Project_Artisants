from django.shortcuts import render
from rest_framework import permissions, serializers, viewsets

from .models import Artisan
from .serializers import (
    ArtisanCreateUpdateSerializer,
    ArtisanSerializer,
)


class ArtisanViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = (
            Artisan.objects
            .select_related("user")
            .prefetch_related("categories")
        )

        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return queryset

        return queryset.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ArtisanCreateUpdateSerializer

        return ArtisanSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "artisan":
            raise serializers.ValidationError(
                "Votre compte doit avoir le rôle artisan."
            )

        if hasattr(user, "artisan_profile"):
            raise serializers.ValidationError(
                "Vous possédez déjà un profil artisan."
            )

        serializer.save(user=user)

    def perform_update(self, serializer):
        artisan = self.get_object()

        if (
            artisan.user != self.request.user
            and not self.request.user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Vous ne pouvez pas modifier cet artisan."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if (
            instance.user != self.request.user
            and not self.request.user.is_staff
        ):
            raise permissions.PermissionDenied(
                "Vous ne pouvez pas supprimer cet artisan."
            )

        instance.is_active = False
        instance.save(update_fields=["is_active"])
