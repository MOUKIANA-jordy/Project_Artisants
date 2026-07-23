from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsDemandOwnerOrReadOnly(BasePermission):
    message = "Vous n'avez pas le droit de modifier cette demande."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        return obj.client == request.user
