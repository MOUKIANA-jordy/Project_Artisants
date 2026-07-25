from rest_framework.permissions import BasePermission


class IsConversationParticipant(BasePermission):
    message = "Vous ne participez pas à cette conversation."

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        user = request.user

        if user.is_staff:
            return True

        return (
            obj.client == user
            or obj.artisan.user == user
        )


class IsMessageParticipant(BasePermission):
    message = "Vous ne pouvez pas accéder à ce message."

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        user = request.user
        conversation = obj.conversation

        if user.is_staff:
            return True

        return (
            conversation.client == user
            or conversation.artisan.user == user
        )
