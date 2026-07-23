from django.shortcuts import render
from rest_framework import permissions, viewsets

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Category.objects.all()

        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by("nom")

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
