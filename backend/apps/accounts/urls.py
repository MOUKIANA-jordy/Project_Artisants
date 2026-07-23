from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    CurrentUserView,
    CustomTokenObtainPairView,
    LogoutView,
    RegisterView,
)


app_name = "accounts"


urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        CustomTokenObtainPairView.as_view(),
        name="login",
    ),
    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "verify/",
        TokenVerifyView.as_view(),
        name="token-verify",
    ),
    path(
        "me/",
        CurrentUserView.as_view(),
        name="me",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
]
