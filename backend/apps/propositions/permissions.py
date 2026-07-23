from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
)


class IsPropositionParticipant(BasePermission):
    message = (
        "Vous n'avez pas le droit d'accéder "
        "à cette proposition."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        user = request.user

        if user.is_staff:
            return True

        if request.method in SAFE_METHODS:
            return (
                obj.artisan.user == user
                or obj.demande.client == user
            )

        return (
            obj.artisan.user == user
            or obj.demande.client == user
        )
