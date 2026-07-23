from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from apps.artisans.views import ArtisanViewSet
from apps.artisans.views_images import ArtisanImageViewSet
from apps.categories.views import CategoryViewSet
from apps.demandes.views import DemandeTravauxViewSet
from apps.demandes.views_images import DemandeImageViewSet
from apps.propositions.views import PropositionViewSet
from apps.reviews.views import ReviewViewSet


router = DefaultRouter()

router.register(
    "categories",
    CategoryViewSet,
    basename="category",
)

router.register(
    "artisans",
    ArtisanViewSet,
    basename="artisan",
)

router.register(
    "demandes",
    DemandeTravauxViewSet,
    basename="demande",
)

router.register(
    "propositions",
    PropositionViewSet,
    basename="proposition",
)

router.register(
    "reviews",
    ReviewViewSet,
    basename="review",
)


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


urlpatterns = (
    router.urls
    + artisans_router.urls
    + demandes_router.urls
)
