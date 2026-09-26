from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from apps.artisans.views import ArtisanViewSet
from apps.artisans.views_images import ArtisanImageViewSet
from apps.categories.views import CategoryViewSet
from apps.demandes.views import DemandeTravauxViewSet
from apps.demandes.views_images import DemandeImageViewSet
from apps.messaging.views import (
    ConversationViewSet,
    MessageViewSet,
)
from apps.notifications.views import NotificationViewSet
from apps.propositions.views import PropositionViewSet
from apps.reviews.views import ReviewViewSet


# ============================================================
# ROUTER PRINCIPAL
# ============================================================

router = DefaultRouter()


# Catégories
router.register(
    "categories",
    CategoryViewSet,
    basename="category",
)


# Artisans
router.register(
    "artisans",
    ArtisanViewSet,
    basename="artisan",
)


# Demandes de travaux
router.register(
    "demandes",
    DemandeTravauxViewSet,
    basename="demande",
)


# Propositions
router.register(
    "propositions",
    PropositionViewSet,
    basename="proposition",
)


# Avis
router.register(
    "reviews",
    ReviewViewSet,
    basename="review",
)


# Conversations
router.register(
    "conversations",
    ConversationViewSet,
    basename="conversation",
)


# Notifications
router.register(
    "notifications",
    NotificationViewSet,
    basename="notification",
)


# ============================================================
# IMAGES DES ARTISANS
# /api/artisans/{artisan_id}/images/
# ============================================================

artisans_router = NestedDefaultRouter(
    router,
    "artisans",
    lookup="artisan",
)

artisans_router.register(
    "images",
    ArtisanImageViewSet,
    basename="artisan-images",
)


# ============================================================
# IMAGES DES DEMANDES
# /api/demandes/{demande_id}/images/
# ============================================================

demandes_router = NestedDefaultRouter(
    router,
    "demandes",
    lookup="demande",
)

demandes_router.register(
    "images",
    DemandeImageViewSet,
    basename="demande-images",
)


# ============================================================
# MESSAGES DES CONVERSATIONS
# /api/conversations/{conversation_id}/messages/
# ============================================================

conversations_router = NestedDefaultRouter(
    router,
    "conversations",
    lookup="conversation",
)

conversations_router.register(
    "messages",
    MessageViewSet,
    basename="conversation-messages",
)


# ============================================================
# URLS
# ============================================================

urlpatterns = (
    router.urls
    + artisans_router.urls
    + demandes_router.urls
    + conversations_router.urls
)
