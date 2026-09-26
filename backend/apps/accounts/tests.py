from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class AccountsAPITests(APITestCase):

    def setUp(self):
        self.password = "TestPassword123!"

        self.user = User.objects.create_user(
            username="jordy_test",
            email="jordy.test@example.com",
            password=self.password,
            first_name="Jordy",
            last_name="Moukiana",
            telephone="0600000000",
            role=User.Role.CLIENT,
        )

    # --------------------------------------------------
    # INSCRIPTION
    # --------------------------------------------------

    def test_register_client(self):
        data = {
            "username": "nouveau_client",
            "email": "nouveau.client@example.com",
            "first_name": "Nouveau",
            "last_name": "Client",
            "telephone": "0611111111",
            "role": "client",
            "password": "StrongPassword123!",
            "password_confirmation": "StrongPassword123!",
        }

        response = self.client.post(
            "/api/auth/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                email="nouveau.client@example.com"
            ).exists()
        )

        user = User.objects.get(
            email="nouveau.client@example.com"
        )

        self.assertEqual(user.role, User.Role.CLIENT)

        # Vérifie que le mot de passe est hashé correctement
        self.assertTrue(
            user.check_password("StrongPassword123!")
        )

    def test_register_artisan(self):
        data = {
            "username": "patrick_test",
            "email": "patrick.test@example.com",
            "first_name": "Patrick",
            "last_name": "Makaya",
            "telephone": "0622222222",
            "role": "artisan",
            "password": "StrongPassword123!",
            "password_confirmation": "StrongPassword123!",
        }

        response = self.client.post(
            "/api/auth/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            email="patrick.test@example.com"
        )

        self.assertEqual(
            user.role,
            User.Role.ARTISAN,
        )

    def test_register_admin_is_forbidden(self):
        data = {
            "username": "fake_admin",
            "email": "fake.admin@example.com",
            "role": "admin",
            "password": "StrongPassword123!",
            "password_confirmation": "StrongPassword123!",
        }

        response = self.client.post(
            "/api/auth/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User.objects.filter(
                email="fake.admin@example.com"
            ).exists()
        )

    def test_register_passwords_do_not_match(self):
        data = {
            "username": "wrong_password",
            "email": "wrong.password@example.com",
            "role": "client",
            "password": "StrongPassword123!",
            "password_confirmation": "DifferentPassword123!",
        }

        response = self.client.post(
            "/api/auth/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User.objects.filter(
                email="wrong.password@example.com"
            ).exists()
        )

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    def test_login_success(self):
        data = {
            "email": self.user.email,
            "password": self.password,
        }

        response = self.client.post(
            "/api/auth/login/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        self.assertEqual(
            response.data["user"]["email"],
            self.user.email,
        )

        self.assertEqual(
            response.data["user"]["role"],
            "client",
        )

    def test_login_wrong_password(self):
        data = {
            "email": self.user.email,
            "password": "WrongPassword123!",
        }

        response = self.client.post(
            "/api/auth/login/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------
    # UTILISATEUR CONNECTÉ
    # --------------------------------------------------

    def test_me_authenticated(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            self.user.email,
        )

        self.assertEqual(
            response.data["username"],
            self.user.username,
        )

        self.assertEqual(
            response.data["role"],
            User.Role.CLIENT,
        )

    def test_me_without_authentication(self):
        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------

    def test_logout_success(self):
        refresh = RefreshToken.for_user(
            self.user
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/auth/logout/",
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_205_RESET_CONTENT,
        )

        self.assertEqual(
            response.data["detail"],
            "Déconnexion réussie.",
        )

    def test_logout_without_refresh_token(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/auth/logout/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["detail"],
            "Le jeton refresh est obligatoire.",
        )

    def test_logout_without_authentication(self):
        refresh = RefreshToken.for_user(
            self.user
        )

        response = self.client.post(
            "/api/auth/logout/",
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
