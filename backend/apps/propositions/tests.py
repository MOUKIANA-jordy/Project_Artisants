from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.artisans.models import Artisan
from apps.categories.models import Category
from apps.demandes.models import DemandeTravaux
from apps.messaging.models import Conversation
from apps.notifications.models import Notification

from .models import Proposition


class PropositionAPITests(APITestCase):

    def setUp(self):
        # --------------------------------------------------
        # UTILISATEURS
        # --------------------------------------------------

        self.client_user = User.objects.create_user(
            username="client_test",
            email="client.test@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.other_client = User.objects.create_user(
            username="other_client",
            email="other.client@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.artisan_user = User.objects.create_user(
            username="artisan_test",
            email="artisan.test@example.com",
            password="TestPassword123!",
            role=User.Role.ARTISAN,
        )

        self.second_artisan_user = User.objects.create_user(
            username="artisan_test_2",
            email="artisan2.test@example.com",
            password="TestPassword123!",
            role=User.Role.ARTISAN,
        )

        # --------------------------------------------------
        # CATÉGORIE
        # --------------------------------------------------

        self.category = Category.objects.create(
            nom="Plomberie",
            slug="plomberie",
            description="Travaux de plomberie",
            is_active=True,
        )

        # --------------------------------------------------
        # PROFILS ARTISANS
        # --------------------------------------------------

        self.artisan = Artisan.objects.create(
            user=self.artisan_user,
            nom_entreprise="Patrick Plomberie",
            description="Artisan plombier",
            ville="Brazzaville",
            quartier="Bacongo",
            experience=5,
        )

        self.artisan.categories.add(
            self.category
        )

        self.second_artisan = Artisan.objects.create(
            user=self.second_artisan_user,
            nom_entreprise="Congo Plomberie",
            description="Deuxième artisan",
            ville="Brazzaville",
            quartier="Poto-Poto",
            experience=3,
        )

        self.second_artisan.categories.add(
            self.category
        )

        # --------------------------------------------------
        # DEMANDE PUBLIÉE
        # --------------------------------------------------

        self.demande = DemandeTravaux.objects.create(
            client=self.client_user,
            categorie=self.category,
            titre="Réparation fuite d'eau",
            description=(
                "Une fuite importante se trouve "
                "sous l'évier."
            ),
            ville="Brazzaville",
            quartier="Bacongo",
            budget_min=15000,
            budget_max=50000,
            date_souhaitee=(
                timezone.localdate()
                + timedelta(days=7)
            ),
            statut=DemandeTravaux.Statut.PUBLIEE,
        )

    def proposition_data(self):
        return {
            "demande_id": self.demande.id,
            "message": (
                "Je peux intervenir rapidement "
                "pour effectuer les travaux."
            ),
            "prix_propose": "30000.00",
            "date_disponibilite": (
                timezone.localdate()
                + timedelta(days=2)
            ).isoformat(),
        }

    # --------------------------------------------------
    # CRÉATION
    # --------------------------------------------------

    def test_artisan_can_create_proposition(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/propositions/",
            self.proposition_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        proposition = Proposition.objects.get(
            artisan=self.artisan,
            demande=self.demande,
        )

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.EN_ATTENTE,
        )

        self.assertEqual(
            proposition.prix_propose,
            30000,
        )

    def test_client_cannot_create_proposition(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/propositions/",
            self.proposition_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Proposition.objects.count(),
            0,
        )

    def test_unauthenticated_user_cannot_create_proposition(
        self,
    ):
        response = self.client.post(
            "/api/propositions/",
            self.proposition_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------
    # DOUBLON
    # --------------------------------------------------

    def test_artisan_cannot_send_two_propositions_for_same_demande(
        self,
    ):
        Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Première proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/propositions/",
            self.proposition_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Proposition.objects.filter(
                demande=self.demande,
                artisan=self.artisan,
            ).count(),
            1,
        )

    # --------------------------------------------------
    # VALIDATION DU PRIX
    # --------------------------------------------------

    def test_price_cannot_be_zero(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        data = self.proposition_data()
        data["prix_propose"] = "0.00"

        response = self.client.post(
            "/api/propositions/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "prix_propose",
            response.data,
        )

    def test_price_cannot_be_negative(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        data = self.proposition_data()
        data["prix_propose"] = "-1000.00"

        response = self.client.post(
            "/api/propositions/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # STATUT DE LA DEMANDE
    # --------------------------------------------------

    def test_artisan_cannot_propose_on_draft_demande(self):
        self.demande.statut = (
            DemandeTravaux.Statut.BROUILLON
        )
        self.demande.save()

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/propositions/",
            self.proposition_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_artisan_cannot_propose_on_completed_demande(self):
        self.demande.statut = (
            DemandeTravaux.Statut.TERMINEE
        )
        self.demande.save()

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/propositions/",
            self.proposition_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # NOTIFICATION APRÈS CRÉATION
    # --------------------------------------------------

    def test_creating_proposition_notifies_client(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/propositions/",
            self.proposition_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        notification = Notification.objects.filter(
            destinataire=self.client_user,
            type=Notification.Type.NOUVELLE_PROPOSITION,
        ).first()

        self.assertIsNotNone(
            notification
        )

    # --------------------------------------------------
    # MODIFICATION
    # --------------------------------------------------

    def test_artisan_can_update_pending_proposition(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Ancien message",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.patch(
            f"/api/propositions/{proposition.id}/",
            {
                "message": "Nouveau message",
                "prix_propose": "35000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        proposition.refresh_from_db()

        self.assertEqual(
            proposition.message,
            "Nouveau message",
        )

        self.assertEqual(
            proposition.prix_propose,
            35000,
        )

    def test_accepted_proposition_cannot_be_modified(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
            statut=Proposition.Statut.ACCEPTEE,
        )

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.patch(
            f"/api/propositions/{proposition.id}/",
            {
                "message": "Modification interdite",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # RETRAIT
    # --------------------------------------------------

    def test_artisan_can_withdraw_pending_proposition(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition à retirer",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.delete(
            f"/api/propositions/{proposition.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        proposition.refresh_from_db()

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.RETIREE,
        )

        self.assertTrue(
            Proposition.objects.filter(
                id=proposition.id
            ).exists()
        )

    # --------------------------------------------------
    # ACCEPTATION
    # --------------------------------------------------

    def test_client_can_accept_proposition(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Je peux faire les travaux.",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/accepter/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        proposition.refresh_from_db()

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.ACCEPTEE,
        )

    def test_accepting_proposition_sets_demande_en_cours(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/accepter/",
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
            DemandeTravaux.Statut.EN_COURS,
        )

    def test_accepting_one_proposition_rejects_others(self):
        proposition1 = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition artisan 1",
            prix_propose=30000,
        )

        proposition2 = Proposition.objects.create(
            demande=self.demande,
            artisan=self.second_artisan,
            message="Proposition artisan 2",
            prix_propose=28000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition1.id}/accepter/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        proposition1.refresh_from_db()
        proposition2.refresh_from_db()

        self.assertEqual(
            proposition1.statut,
            Proposition.Statut.ACCEPTEE,
        )

        self.assertEqual(
            proposition2.statut,
            Proposition.Statut.REFUSEE,
        )

    # --------------------------------------------------
    # CONVERSATION
    # --------------------------------------------------

    def test_accepting_proposition_creates_conversation(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/accepter/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        conversation = Conversation.objects.filter(
            demande=self.demande,
            client=self.client_user,
            artisan=self.artisan,
        ).first()

        self.assertIsNotNone(
            conversation
        )

    # --------------------------------------------------
    # NOTIFICATION D'ACCEPTATION
    # --------------------------------------------------

    def test_accepting_proposition_notifies_artisan(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/accepter/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification = Notification.objects.filter(
            destinataire=self.artisan_user,
            type=Notification.Type.PROPOSITION_ACCEPTEE,
        ).first()

        self.assertIsNotNone(
            notification
        )

    # --------------------------------------------------
    # REFUS
    # --------------------------------------------------

    def test_client_can_reject_proposition(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/refuser/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        proposition.refresh_from_db()

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.REFUSEE,
        )

    def test_rejecting_proposition_notifies_artisan(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/refuser/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification = Notification.objects.filter(
            destinataire=self.artisan_user,
            type=Notification.Type.PROPOSITION_REFUSEE,
        ).first()

        self.assertIsNotNone(
            notification
        )

    # --------------------------------------------------
    # PERMISSIONS
    # --------------------------------------------------

    def test_other_client_cannot_accept_proposition(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.other_client
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/accepter/",
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

        proposition.refresh_from_db()

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.EN_ATTENTE,
        )

    def test_artisan_cannot_accept_own_proposition(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            f"/api/propositions/{proposition.id}/accepter/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        proposition.refresh_from_db()

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.EN_ATTENTE,
        )

    # --------------------------------------------------
    # LISTES
    # --------------------------------------------------

    def test_artisan_can_see_sent_propositions(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Ma proposition",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.get(
            "/api/propositions/envoyees/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            proposition.id,
            ids,
        )

    def test_client_can_see_received_propositions(self):
        proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Proposition reçue",
            prix_propose=30000,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.get(
            "/api/propositions/recues/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            proposition.id,
            ids,
        )
