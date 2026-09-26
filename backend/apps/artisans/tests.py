from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.categories.models import Category

from .models import Artisan


class ArtisanAPITests(APITestCase):

    def setUp(self):
        self.artisan_user = User.objects.create_user(
            username="artisan_test",
            email="artisan.test@example.com",
            password="TestPassword123!",
            role=User.Role.ARTISAN,
        )

        self.other_artisan_user = User.objects.create_user(
            username="other_artisan",
            email="other.artisan@example.com",
            password="TestPassword123!",
            role=User.Role.ARTISAN,
        )

        self.client_user = User.objects.create_user(
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

        self.category = Category.objects.create(
            nom="Plomberie",
            slug="plomberie",
            is_active=True,
        )

        self.inactive_category = Category.objects.create(
            nom="Ancienne catégorie",
            slug="ancienne-categorie",
            is_active=False,
        )

    def artisan_data(self):
        return {
            "nom_entreprise": "Patrick Plomberie",
            "description": "Artisan plombier",
            "category_ids": [
                self.category.id
            ],
            "ville": "Brazzaville",
            "quartier": "Bacongo",
            "experience": 5,
        }

    def create_artisan(self):
        artisan = Artisan.objects.create(
            user=self.artisan_user,
            nom_entreprise="Patrick Plomberie",
            description="Artisan plombier",
            ville="Brazzaville",
            quartier="Bacongo",
            experience=5,
        )

        artisan.categories.add(
            self.category
        )

        return artisan

    # --------------------------------------------------
    # CRÉATION
    # --------------------------------------------------

    def test_artisan_user_can_create_profile(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/artisans/",
            self.artisan_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        artisan = Artisan.objects.get(
            user=self.artisan_user
        )

        self.assertEqual(
            artisan.nom_entreprise,
            "Patrick Plomberie",
        )

        self.assertTrue(
            artisan.categories.filter(
                id=self.category.id
            ).exists()
        )

    def test_client_cannot_create_artisan_profile(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/artisans/",
            self.artisan_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Artisan.objects.filter(
                user=self.client_user
            ).exists()
        )

    def test_unauthenticated_user_cannot_create_artisan(self):
        response = self.client.post(
            "/api/artisans/",
            self.artisan_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_artisan_cannot_create_second_profile(self):
        self.create_artisan()

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/artisans/",
            self.artisan_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Artisan.objects.filter(
                user=self.artisan_user
            ).count(),
            1,
        )

    # --------------------------------------------------
    # CATÉGORIES
    # --------------------------------------------------

    def test_artisan_cannot_use_inactive_category(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        data = self.artisan_data()

        data["category_ids"] = [
            self.inactive_category.id
        ]

        response = self.client.post(
            "/api/artisans/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # EXPÉRIENCE
    # --------------------------------------------------

    def test_experience_over_80_is_rejected(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        data = self.artisan_data()
        data["experience"] = 81

        response = self.client.post(
            "/api/artisans/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # COORDONNÉES GPS
    # --------------------------------------------------

    def test_latitude_without_longitude_is_rejected(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        data = self.artisan_data()
        data["latitude"] = -4.2634

        response = self.client.post(
            "/api/artisans/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_latitude_and_longitude_are_accepted_together(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        data = self.artisan_data()

        data["latitude"] = -4.2634
        data["longitude"] = 15.2429

        response = self.client.post(
            "/api/artisans/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    # --------------------------------------------------
    # LECTURE
    # --------------------------------------------------

    def test_anonymous_user_can_list_active_artisans(self):
        artisan = self.create_artisan()

        response = self.client.get(
            "/api/artisans/"
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
            artisan.id,
            ids,
        )

    def test_anonymous_user_cannot_see_inactive_artisans(self):
        artisan = self.create_artisan()

        artisan.is_active = False
        artisan.save()

        response = self.client.get(
            "/api/artisans/"
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
            artisan.id,
            ids,
        )

    def test_staff_can_see_inactive_artisans(self):
        artisan = self.create_artisan()

        artisan.is_active = False
        artisan.save()

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/artisans/"
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
            artisan.id,
            ids,
        )

    # --------------------------------------------------
    # MODIFICATION
    # --------------------------------------------------

    def test_owner_can_update_artisan_profile(self):
        artisan = self.create_artisan()

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.patch(
            f"/api/artisans/{artisan.id}/",
            {
                "nom_entreprise": (
                    "Patrick Plomberie Services"
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        artisan.refresh_from_db()

        self.assertEqual(
            artisan.nom_entreprise,
            "Patrick Plomberie Services",
        )

    def test_other_artisan_cannot_update_profile(self):
        artisan = self.create_artisan()

        self.client.force_authenticate(
            user=self.other_artisan_user
        )

        response = self.client.patch(
            f"/api/artisans/{artisan.id}/",
            {
                "nom_entreprise": "Entreprise piratée"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        artisan.refresh_from_db()

        self.assertEqual(
            artisan.nom_entreprise,
            "Patrick Plomberie",
        )

    # --------------------------------------------------
    # SUPPRESSION LOGIQUE
    # --------------------------------------------------

    def test_owner_can_soft_delete_artisan_profile(self):
        artisan = self.create_artisan()

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.delete(
            f"/api/artisans/{artisan.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        artisan.refresh_from_db()

        self.assertFalse(
            artisan.is_active
        )

        self.assertTrue(
            Artisan.objects.filter(
                id=artisan.id
            ).exists()
        )

    def test_other_artisan_cannot_delete_profile(self):
        artisan = self.create_artisan()

        self.client.force_authenticate(
            user=self.other_artisan_user
        )

        response = self.client.delete(
            f"/api/artisans/{artisan.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        artisan.refresh_from_db()

        self.assertTrue(
            artisan.is_active
        )
