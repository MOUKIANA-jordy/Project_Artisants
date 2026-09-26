from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def accueil(request):
    return JsonResponse(
        {
            "application": "Annuaire des Artisans",
            "version": "1.0.0",
            "status": "en ligne",
            "database": "MySQL",
            "framework": "Django REST Framework",
            "routes": {
                "admin": "/admin/",
                "api": "/api/",
                "auth": {
                    "register": "/api/auth/register/",
                    "login": "/api/auth/login/",
                    "refresh": "/api/auth/refresh/",
                    "me": "/api/auth/me/",
                },
                "categories": "/api/categories/",
                "artisans": "/api/artisans/",
                "demandes": "/api/demandes/",
                "propositions": "/api/propositions/",
                "reviews": "/api/reviews/",
                "conversations": "/api/conversations/",
                "notifications": "/api/notifications/",
            },
        }
    )


urlpatterns = [
    path("", accueil, name="accueil"),
    path("admin/", admin.site.urls),
    path("api/", include("config.api_urls")),
    path("api/auth/", include("apps.accounts.urls")),
]
