from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.artisans.models import Artisan
from apps.categories.models import Category
from apps.demandes.models import DemandeTravaux
from apps.messaging.models import Conversation, Message
from apps.notifications.models import Notification
from apps.propositions.models import Proposition
from apps.reviews.models import Review


class CompleteWorkflowIntegrationTest(APITestCase):
    """
    Test d'intégration du parcours métier complet :

    Client
        -> crée une demande
        -> publie la demande

    Artisan
        -> crée son profil
        -> envoie une proposition

    Client
        -> accepte la proposition

    Système
        -> passe la demande en cours
        -> crée une conversation
        -> crée les notifications

    Client / Artisan
        -> échangent un message

    Client
        -> termine les travaux
        -> laisse un avis

    Système
        -> notifie l'artisan
    """

    def setUp(self):
        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        self.admin = User.objects.create_user(
            username="admin_test",
            email="admin.integration@example.com",
            password="TestPassword123!",
            role=User.Role.ADMIN,
            is_staff=True,
        )

        # --------------------------------------------------
        # CLIENT
        # --------------------------------------------------

        self.client_user = User.objects.create_user(
            username="client_integration",
            email="client.integration@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        # --------------------------------------------------
        # ARTISAN
        # --------------------------------------------------

        self.artisan_user = User.objects.create_user(
            username="artisan_integration",
            email="artisan.integration@example.com",
            password="TestPassword123!",
            role=User.Role.ARTISAN,
        )

        # --------------------------------------------------
        # CATÉGORIE
        #
        # On la crée directement ici car les permissions
        # d'API des catégories ont déjà leurs propres tests.
        # --------------------------------------------------

        self.category = Category.objects.create(
            nom="Plomberie",
            slug="plomberie",
            description="Travaux de plomberie",
            is_active=True,
        )

    def test_complete_client_artisan_workflow(self):

        # ==================================================
        # ÉTAPE 1
        # L'ARTISAN CRÉE SON PROFIL
        # ==================================================

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/artisans/",
            {
                "nom_entreprise": (
                    "Patrick Plomberie Services"
                ),
                "description": (
                    "Artisan spécialisé en plomberie."
                ),
                "category_ids": [
                    self.category.id
                ],
                "ville": "Brazzaville",
                "quartier": "Bacongo",
                "experience": 8,
            },
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
            "Patrick Plomberie Services",
        )

        self.assertTrue(
            artisan.categories.filter(
                id=self.category.id
            ).exists()
        )

        # ==================================================
        # ÉTAPE 2
        # LE CLIENT CRÉE UNE DEMANDE
        # ==================================================

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/demandes/",
            {
                "categorie_id": self.category.id,
                "titre": "Réparation fuite d'eau",
                "description": (
                    "Une fuite importante est présente "
                    "dans la salle de bain."
                ),
                "ville": "Brazzaville",
                "quartier": "Bacongo",
                "adresse": "10 rue Test",
                "budget_min": "20000.00",
                "budget_max": "50000.00",
                "is_urgent": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        demande_id = response.data["id"]

        demande = DemandeTravaux.objects.get(
            id=demande_id
        )

        self.assertEqual(
            demande.client,
            self.client_user,
        )

        self.assertEqual(
            demande.statut,
            DemandeTravaux.Statut.BROUILLON,
        )

        # ==================================================
        # ÉTAPE 3
        # LE CLIENT PUBLIE SA DEMANDE
        # ==================================================

        response = self.client.post(
            f"/api/demandes/{demande.id}/publier/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        demande.refresh_from_db()

        self.assertEqual(
            demande.statut,
            DemandeTravaux.Statut.PUBLIEE,
        )

        # ==================================================
        # ÉTAPE 4
        # L'ARTISAN ENVOIE UNE PROPOSITION
        # ==================================================

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/propositions/",
            {
                "demande_id": demande.id,
                "message": (
                    "Bonjour, je peux intervenir "
                    "rapidement pour réparer cette fuite."
                ),
                "prix_propose": "35000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        proposition_id = response.data["id"]

        proposition = Proposition.objects.get(
            id=proposition_id
        )

        self.assertEqual(
            proposition.artisan,
            artisan,
        )

        self.assertEqual(
            proposition.demande,
            demande,
        )

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.EN_ATTENTE,
        )

        # ==================================================
        # ÉTAPE 5
        # LE CLIENT DOIT AVOIR REÇU UNE NOTIFICATION
        # ==================================================

        self.assertTrue(
            Notification.objects.filter(
                destinataire=self.client_user,
                type=(
                    Notification.Type.NOUVELLE_PROPOSITION
                ),
            ).exists()
        )

        # ==================================================
        # ÉTAPE 6
        # LE CLIENT ACCEPTE LA PROPOSITION
        # ==================================================

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            (
                f"/api/propositions/"
                f"{proposition.id}/accepter/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        proposition.refresh_from_db()
        demande.refresh_from_db()

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.ACCEPTEE,
        )

        self.assertEqual(
            demande.statut,
            DemandeTravaux.Statut.EN_COURS,
        )

        # ==================================================
        # ÉTAPE 7
        # UNE CONVERSATION DOIT ÊTRE CRÉÉE
        # ==================================================

        conversation = Conversation.objects.get(
            demande=demande
        )

        self.assertEqual(
            conversation.client,
            self.client_user,
        )

        self.assertEqual(
            conversation.artisan,
            artisan,
        )

        self.assertTrue(
            conversation.is_active
        )

        # ==================================================
        # ÉTAPE 8
        # L'ARTISAN DOIT ÊTRE NOTIFIÉ DE L'ACCEPTATION
        # ==================================================

        self.assertTrue(
            Notification.objects.filter(
                destinataire=self.artisan_user,
                type=(
                    Notification.Type.PROPOSITION_ACCEPTEE
                ),
            ).exists()
        )

        # ==================================================
        # ÉTAPE 9
        # LE CLIENT ENVOIE UN MESSAGE
        # ==================================================

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            (
                f"/api/conversations/"
                f"{conversation.id}/messages/"
            ),
            {
                "contenu": (
                    "Bonjour, pouvez-vous intervenir "
                    "demain matin ?"
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        message = Message.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            message.sender,
            self.client_user,
        )

        self.assertEqual(
            message.conversation,
            conversation,
        )

        # ==================================================
        # ÉTAPE 10
        # L'ARTISAN REÇOIT UNE NOTIFICATION MESSAGE
        # ==================================================

        self.assertTrue(
            Notification.objects.filter(
                destinataire=self.artisan_user,
                type=Notification.Type.NOUVEAU_MESSAGE,
            ).exists()
        )

        # ==================================================
        # ÉTAPE 11
        # L'ARTISAN RÉPOND
        # ==================================================

        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            (
                f"/api/conversations/"
                f"{conversation.id}/messages/"
            ),
            {
                "contenu": (
                    "Oui, je peux intervenir "
                    "demain à 9h."
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Message.objects.filter(
                conversation=conversation
            ).count(),
            2,
        )

        # ==================================================
        # ÉTAPE 12
        # LE CLIENT REÇOIT LA NOTIFICATION DU MESSAGE
        # ==================================================

        self.assertTrue(
            Notification.objects.filter(
                destinataire=self.client_user,
                type=Notification.Type.NOUVEAU_MESSAGE,
            ).exists()
        )

        # ==================================================
        # ÉTAPE 13
        # LE CLIENT TERMINE LES TRAVAUX
        # ==================================================

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            f"/api/demandes/{demande.id}/terminer/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        demande.refresh_from_db()

        self.assertEqual(
            demande.statut,
            DemandeTravaux.Statut.TERMINEE,
        )

        # ==================================================
        # ÉTAPE 14
        # LE CLIENT LAISSE UN AVIS 5/5
        # ==================================================

        response = self.client.post(
            "/api/reviews/",
            {
                "demande_id": demande.id,
                "rating": 5,
                "commentaire": (
                    "Très bon travail, intervention "
                    "rapide et professionnelle."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        review = Review.objects.get(
            demande=demande
        )

        self.assertEqual(
            review.client,
            self.client_user,
        )

        self.assertEqual(
            review.artisan,
            artisan,
        )

        self.assertEqual(
            review.rating,
            5,
        )

        # ==================================================
        # ÉTAPE 15
        # L'ARTISAN REÇOIT LA NOTIFICATION DU NOUVEL AVIS
        # ==================================================

        self.assertTrue(
            Notification.objects.filter(
                destinataire=self.artisan_user,
                type=Notification.Type.NOUVEL_AVIS,
            ).exists()
        )

        # ==================================================
        # ÉTAPE 16
        # VÉRIFICATION FINALE
        # ==================================================

        demande.refresh_from_db()
        proposition.refresh_from_db()
        conversation.refresh_from_db()
        review.refresh_from_db()

        self.assertEqual(
            demande.statut,
            DemandeTravaux.Statut.TERMINEE,
        )

        self.assertEqual(
            proposition.statut,
            Proposition.Statut.ACCEPTEE,
        )

        self.assertEqual(
            conversation.demande,
            demande,
        )

        self.assertEqual(
            Message.objects.filter(
                conversation=conversation
            ).count(),
            2,
        )

        self.assertEqual(
            review.rating,
            5,
        )

        self.assertGreaterEqual(
            Notification.objects.count(),
            4,
        )
