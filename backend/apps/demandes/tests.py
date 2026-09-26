from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.categories.models import Category

from .models import DemandeTravaux


class DemandeTravauxAPITests(APITestCase):

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client_test",
            email="client.test@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.other_client = User.objects.create_user(
            username="autre_client",
            email="autre.client@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.artisan_user = User.objects.create_user(
            username="artisan_test",
            email="artisan.test@example.com",
            password="TestPassword123!",
            role=User.Role.ARTISAN,
        )

        self.category = Category.objects.create(
            nom="Plomberie",
            slug="plomberie",
            description="Travaux de plomberie",
            is_active=True,
        )

        self.demande = DemandeTravaux.objects.create(
            client=self.client_user,
            categorie=self.category,
            titre="Réparer une fuite",
            description="Une fuite se trouve sous l'évier.",
            ville="Brazzaville",
            quartier="Bacongo",
            budget_min=15000,
            budget_max=50000,
            date_souhaitee=timezone.localdate()
            + timedelta(days=7),
            statut=DemandeTravaux.Statut.BROUILLON,
        )

    def demande_data(self):
        return {
            "categorie_id": self.category.id,
            "titre": "Réparation plomberie",
            "description": "Réparer une importante fuite d'eau.",
            "ville": "Brazzaville",
            "quartier": "Poto-Poto",
            "adresse": "Avenue de la Paix",
            "budget_min": "10000.00",
            "budget_max": "50000.00",
            "date_souhaitee": (
                timezone.localdate() + timedelta(days=10)
            ).isoformat(),
            "is_urgent": False,
        }

    # --------------------------------------------------
    # CRÉATION
    # --------------------------------------------------

    def test_client_can_create_demande(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/demandes/",
            self.demande_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        demande = DemandeTravaux.objects.get(
            titre="Réparation plomberie"
        )

        self.assertEqual(
            demande.client,
            self.client_user,
        )

        self.assertEqual(
            demande.statut,
            DemandeTravaux.Statut.BROUILLON,
        )

    def test_artisan_cannot_create_demande(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/demandes/",
            self.demande_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            DemandeTravaux.objects.filter(
                titre="Réparation plomberie"
            ).exists()
        )

    def test_unauthenticated_user_cannot_create_demande(self):
        response = self.client.post(
            "/api/demandes/",
            self.demande_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    def test_budget_min_cannot_be_greater_than_budget_max(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        data = self.demande_data()
        data["budget_min"] = "60000.00"
        data["budget_max"] = "10000.00"

        response = self.client.post(
            "/api/demandes/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "budget_max",
            response.data,
        )

    def test_budget_cannot_be_negative(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        data = self.demande_data()
        data["budget_min"] = "-1000.00"

        response = self.client.post(
            "/api/demandes/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_date_souhaitee_cannot_be_in_past(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        data = self.demande_data()

        data["date_souhaitee"] = (
            timezone.localdate()
            - timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            "/api/demandes/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "date_souhaitee",
            response.data,
        )

    # --------------------------------------------------
    # PUBLICATION
    # --------------------------------------------------

    def test_owner_can_publish_draft_demande(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/demandes/{self.demande.id}/publier/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.demande.refresh_from_db()

        self.assertEqual(
            self.demande.statut,
            DemandeTravaux.Statut.PUBLIEE,
        )

    def test_published_demande_cannot_be_published_again(self):
        self.demande.statut = (
            DemandeTravaux.Statut.PUBLIEE
        )
        self.demande.save()

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/demandes/{self.demande.id}/publier/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_other_client_cannot_publish_demande(self):
        self.client.force_authenticate(
            user=self.other_client
        )

        response = self.client.post(
            f"/api/demandes/{self.demande.id}/publier/",
            {},
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ],
        )

        self.demande.refresh_from_db()

        self.assertEqual(
            self.demande.statut,
            DemandeTravaux.Statut.BROUILLON,
        )

    # --------------------------------------------------
    # MODIFICATION
    # --------------------------------------------------

    def test_owner_can_update_demande(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.patch(
            f"/api/demandes/{self.demande.id}/",
            {
                "titre": "Nouveau titre",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.demande.refresh_from_db()

        self.assertEqual(
            self.demande.titre,
            "Nouveau titre",
        )

    def test_other_client_cannot_update_demande(self):
        self.client.force_authenticate(
            user=self.other_client
        )

        response = self.client.patch(
            f"/api/demandes/{self.demande.id}/",
            {
                "titre": "Modification interdite",
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ],
        )

        self.demande.refresh_from_db()

        self.assertNotEqual(
            self.demande.titre,
            "Modification interdite",
        )

    def test_terminated_demande_cannot_be_modified(self):
        self.demande.statut = (
            DemandeTravaux.Statut.TERMINEE
        )
        self.demande.save()

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.patch(
            f"/api/demandes/{self.demande.id}/",
            {
                "titre": "Modification interdite",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # ANNULATION
    # --------------------------------------------------

    def test_owner_can_cancel_demande(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/demandes/{self.demande.id}/annuler/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.demande.refresh_from_db()

        self.assertEqual(
            self.demande.statut,
            DemandeTravaux.Statut.ANNULEE,
        )

    def test_cancelled_demande_cannot_be_cancelled_again(self):
        self.demande.statut = (
            DemandeTravaux.Statut.ANNULEE
        )
        self.demande.save()

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/demandes/{self.demande.id}/annuler/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # TERMINER
    # --------------------------------------------------

    def test_draft_demande_cannot_be_terminated(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/demandes/{self.demande.id}/terminer/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.demande.refresh_from_db()

        self.assertEqual(
            self.demande.statut,
            DemandeTravaux.Statut.BROUILLON,
        )

    def test_en_cours_without_accepted_proposition_cannot_be_terminated(
        self,
    ):
        self.demande.statut = (
            DemandeTravaux.Statut.EN_COURS
        )
        self.demande.save()

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/demandes/{self.demande.id}/terminer/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.demande.refresh_from_db()

        self.assertEqual(
            self.demande.statut,
            DemandeTravaux.Statut.EN_COURS,
        )

    # --------------------------------------------------
    # VISIBILITÉ
    # --------------------------------------------------

    def test_anonymous_user_cannot_see_draft_demande(self):
        response = self.client.get(
            f"/api/demandes/{self.demande.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_anonymous_user_can_see_published_demande(self):
        self.demande.statut = (
            DemandeTravaux.Statut.PUBLIEE
        )
        self.demande.save()

        response = self.client.get(
            f"/api/demandes/{self.demande.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_mes_demandes_returns_only_current_user_demands(self):
        DemandeTravaux.objects.create(
            client=self.other_client,
            categorie=self.category,
            titre="Demande autre client",
            description="Cette demande appartient à un autre client.",
            ville="Brazzaville",
            statut=DemandeTravaux.Statut.BROUILLON,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.get(
            "/api/demandes/mes-demandes/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data.get(
            "results",
            response.data,
        )

        ids = [
            demande["id"]
            for demande in results
        ]

        self.assertIn(
            self.demande.id,
            ids,
        )

        autre_demande = DemandeTravaux.objects.get(
            titre="Demande autre client"
        )

        self.assertNotIn(
            autre_demande.id,
            ids,
        )
