from .models import Notification


def create_notification(
    *,
    destinataire,
    type_notification,
    titre,
    message,
    lien="",
):
    return Notification.objects.create(
        destinataire=destinataire,
        type=type_notification,
        titre=titre,
        message=message,
        lien=lien,
    )
