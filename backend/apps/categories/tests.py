from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Category


class CategoryAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="client_test",
            email="client.test@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.admin = User.objects.create_user(
            username="admin_test",
            email="admin.test@example.com",
            password="TestPassword123!",
            role=User.Role.ADMIN,
            is_staff=True,
        )

        self.active_category = Category.objects.create(
            nom="Plomberie",
            slug="plomberie",
            description="Travaux de plomberie",
            is_active=True,
        )

        self.inactive_category = Category.objects.create(
            nom="Électricité",
            slug="electricite",
            description="Travaux électriques",
            is_active=False,
        )

    # --------------------------------------------------
    # LECTURE PUBLIQUE
    # --------------------------------------------------

    def test_anonymous_user_can_list_active_categories(self):
        response = self.client.get(
            "/api/categories/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data["results"]
            if isinstance(response.data, dict)
            and "results" in response.data
            else response.data
        )

        ids = [
            item["id"]
            for item in results
        ]

        self.assertIn(
            self.active_category.id,
            ids,
        )

    def test_anonymous_user_cannot_see_inactive_categories(self):
        response = self.client.get(
            "/api/categories/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data["results"]
            if isinstance(response.data, dict)
            and "results" in response.data
            else response.data
        )

        ids = [
            item["id"]
            for item in results
        ]

        self.assertNotIn(
            self.inactive_category.id,
            ids,
        )

    def test_normal_user_cannot_see_inactive_categories(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/categories/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data["results"]
            if isinstance(response.data, dict)
            and "results" in response.data
            else response.data
        )

        ids = [
            item["id"]
            for item in results
        ]

        self.assertIn(
            self.active_category.id,
            ids,
        )

        self.assertNotIn(
            self.inactive_category.id,
            ids,
        )

    def test_staff_can_see_inactive_categories(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/categories/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data["results"]
            if isinstance(response.data, dict)
            and "results" in response.data
            else response.data
        )

        ids = [
            item["id"]
            for item in results
        ]

        self.assertIn(
            self.active_category.id,
            ids,
        )

        self.assertIn(
            self.inactive_category.id,
            ids,
        )

    # --------------------------------------------------
    # CRÉATION
    # --------------------------------------------------

    def test_unauthenticated_user_cannot_create_category(self):
        response = self.client.post(
            "/api/categories/",
            {
                "nom": "Peinture",
                "slug": "peinture",
                "description": "Travaux de peinture",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            Category.objects.filter(
                slug="peinture"
            ).exists()
        )

    def test_normal_user_cannot_create_category(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/categories/",
            {
                "nom": "Peinture",
                "slug": "peinture",
                "description": "Travaux de peinture",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Category.objects.filter(
                slug="peinture"
            ).exists()
        )

    def test_admin_can_create_category(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            "/api/categories/",
            {
                "nom": "Peinture",
                "slug": "peinture",
                "description": "Travaux de peinture",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Category.objects.filter(
                slug="peinture"
            ).exists()
        )

    # --------------------------------------------------
    # MODIFICATION
    # --------------------------------------------------

    def test_normal_user_cannot_update_category(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"/api/categories/{self.active_category.id}/",
            {
                "nom": "Plomberie modifiée",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.active_category.refresh_from_db()

        self.assertEqual(
            self.active_category.nom,
            "Plomberie",
        )

    def test_admin_can_update_category(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.patch(
            f"/api/categories/{self.active_category.id}/",
            {
                "nom": "Plomberie générale",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.active_category.refresh_from_db()

        self.assertEqual(
            self.active_category.nom,
            "Plomberie générale",
        )

    # --------------------------------------------------
    # SUPPRESSION LOGIQUE
    # --------------------------------------------------

    def test_normal_user_cannot_delete_category(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"/api/categories/{self.active_category.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.active_category.refresh_from_db()

        self.assertTrue(
            self.active_category.is_active
        )

    def test_admin_can_soft_delete_category(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.delete(
            f"/api/categories/{self.active_category.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.active_category.refresh_from_db()

        self.assertFalse(
            self.active_category.is_active
        )

        self.assertTrue(
            Category.objects.filter(
                id=self.active_category.id
            ).exists()
        )

    # --------------------------------------------------
    # ORDRE
    # --------------------------------------------------

    def test_categories_are_ordered_by_name(self):
        Category.objects.create(
            nom="Maçonnerie",
            slug="maconnerie",
            description="Travaux de maçonnerie",
            is_active=True,
        )

        response = self.client.get(
            "/api/categories/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data["results"]
            if isinstance(response.data, dict)
            and "results" in response.data
            else response.data
        )

        names = [
            item["nom"]
            for item in results
        ]

        self.assertEqual(
            names,
            sorted(names),
        )
