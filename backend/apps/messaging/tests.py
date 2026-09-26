from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.artisans.models import Artisan
from apps.categories.models import Category
from apps.demandes.models import DemandeTravaux
from apps.notifications.models import Notification

from .models import Conversation, Message


class MessagingAPITests(APITestCase):

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

        self.artisan_user = User.objects.create_user(
            username="artisan_test",
            email="artisan.test@example.com",
            password="TestPassword123!",
            role=User.Role.ARTISAN,
        )

        self.other_user = User.objects.create_user(
            username="other_user",
            email="other.test@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
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
        # ARTISAN
        # --------------------------------------------------

        self.artisan = Artisan.objects.create(
            user=self.artisan_user,
            nom_entreprise="Patrick Plomberie",
            description="Artisan plombier",
            ville="Brazzaville",
            quartier="Bacongo",
            experience=5,
        )

        self.artisan.categories.add(self.category)

        # --------------------------------------------------
        # DEMANDE
        # --------------------------------------------------

        self.demande = DemandeTravaux.objects.create(
            client=self.client_user,
            categorie=self.category,
            titre="Réparation fuite",
            description="Réparation d'une fuite d'eau.",
            ville="Brazzaville",
            quartier="Bacongo",
            statut=DemandeTravaux.Statut.EN_COURS,
        )

        # --------------------------------------------------
        # CONVERSATION
        # --------------------------------------------------

        self.conversation = Conversation.objects.create(
            demande=self.demande,
            client=self.client_user,
            artisan=self.artisan,
        )

    def messages_url(self):
        return (
            f"/api/conversations/"
            f"{self.conversation.id}/messages/"
        )

    # --------------------------------------------------
    # ACCÈS AUX CONVERSATIONS
    # --------------------------------------------------

    def test_client_can_see_conversation(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.get(
            f"/api/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_artisan_can_see_conversation(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.get(
            f"/api/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_other_user_cannot_see_conversation(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.get(
            f"/api/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unauthenticated_user_cannot_see_conversation(self):
        response = self.client.get(
            f"/api/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------
    # ENVOI DE MESSAGES
    # --------------------------------------------------

    def test_client_can_send_message(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": (
                    "Bonjour, quand pouvez-vous intervenir ?"
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        message = Message.objects.get()

        self.assertEqual(
            message.sender,
            self.client_user,
        )

        self.assertEqual(
            message.conversation,
            self.conversation,
        )

        self.assertFalse(message.is_read)

    def test_artisan_can_send_message(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": (
                    "Bonjour, je peux intervenir demain."
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        message = Message.objects.get()

        self.assertEqual(
            message.sender,
            self.artisan_user,
        )

    def test_other_user_cannot_send_message(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": "Message interdit."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            Message.objects.count(),
            0,
        )

    def test_unauthenticated_user_cannot_send_message(self):
        response = self.client.post(
            self.messages_url(),
            {
                "contenu": "Message interdit."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------
    # VALIDATION DU CONTENU
    # --------------------------------------------------

    def test_empty_message_is_rejected(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": "   "
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "contenu",
            response.data,
        )

    def test_message_over_5000_characters_is_rejected(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": "a" * 5001
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # CONVERSATION FERMÉE
    # --------------------------------------------------

    def test_cannot_send_message_to_inactive_conversation(self):
        self.conversation.is_active = False
        self.conversation.save()

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": "Bonjour"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Message.objects.count(),
            0,
        )

    # --------------------------------------------------
    # NOTIFICATIONS
    # --------------------------------------------------

    def test_client_message_notifies_artisan(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": "Bonjour Patrick."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        notification = Notification.objects.filter(
            destinataire=self.artisan_user,
            type=Notification.Type.NOUVEAU_MESSAGE,
        ).first()

        self.assertIsNotNone(notification)

    def test_artisan_message_notifies_client(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            self.messages_url(),
            {
                "contenu": "Bonjour, je suis disponible."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        notification = Notification.objects.filter(
            destinataire=self.client_user,
            type=Notification.Type.NOUVEAU_MESSAGE,
        ).first()

        self.assertIsNotNone(notification)

    # --------------------------------------------------
    # LISTE DES MESSAGES
    # --------------------------------------------------

    def test_client_can_list_messages(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.artisan_user,
            contenu="Bonjour client.",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.get(
            self.messages_url()
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
            item["id"]
            for item in results
        ]

        self.assertIn(
            message.id,
            ids,
        )

    def test_other_user_cannot_list_messages(self):
        Message.objects.create(
            conversation=self.conversation,
            sender=self.client_user,
            contenu="Message privé.",
        )

        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.get(
            self.messages_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data.get(
            "results",
            response.data,
        )

        self.assertEqual(
            len(results),
            0,
        )

    # --------------------------------------------------
    # MARQUER COMME LUS
    # --------------------------------------------------

    def test_client_can_mark_artisan_messages_as_read(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.artisan_user,
            contenu="Message artisan.",
            is_read=False,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            (
                f"/api/conversations/"
                f"{self.conversation.id}/marquer-lus/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        message.refresh_from_db()

        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)

    def test_mark_read_does_not_mark_own_messages(self):
        own_message = Message.objects.create(
            conversation=self.conversation,
            sender=self.client_user,
            contenu="Mon message.",
            is_read=False,
        )

        received_message = Message.objects.create(
            conversation=self.conversation,
            sender=self.artisan_user,
            contenu="Message reçu.",
            is_read=False,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            (
                f"/api/conversations/"
                f"{self.conversation.id}/marquer-lus/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        own_message.refresh_from_db()
        received_message.refresh_from_db()

        self.assertFalse(
            own_message.is_read
        )

        self.assertTrue(
            received_message.is_read
        )

    # --------------------------------------------------
    # COMPTEUR NON LUS
    # --------------------------------------------------

    def test_conversation_counts_unread_received_messages(self):
        Message.objects.create(
            conversation=self.conversation,
            sender=self.artisan_user,
            contenu="Non lu 1",
            is_read=False,
        )

        Message.objects.create(
            conversation=self.conversation,
            sender=self.artisan_user,
            contenu="Non lu 2",
            is_read=False,
        )

        Message.objects.create(
            conversation=self.conversation,
            sender=self.client_user,
            contenu="Mon propre message",
            is_read=False,
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.get(
            f"/api/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["messages_non_lus"],
            2,
        )

    # --------------------------------------------------
    # DERNIER MESSAGE
    # --------------------------------------------------

    def test_conversation_returns_last_message(self):
        Message.objects.create(
            conversation=self.conversation,
            sender=self.client_user,
            contenu="Premier message",
        )

        last_message = Message.objects.create(
            conversation=self.conversation,
            sender=self.artisan_user,
            contenu="Dernier message",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.get(
            f"/api/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["dernier_message"]["id"],
            last_message.id,
        )

        self.assertEqual(
            response.data["dernier_message"]["contenu"],
            "Dernier message",
        )

    # --------------------------------------------------
    # SUPPRESSION
    # --------------------------------------------------

    def test_sender_can_delete_own_message(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.client_user,
            contenu="Message à supprimer.",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.delete(
            (
                f"/api/conversations/"
                f"{self.conversation.id}/messages/"
                f"{message.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Message.objects.filter(
                id=message.id
            ).exists()
        )

    def test_participant_cannot_delete_other_person_message(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.artisan_user,
            contenu="Message de l'artisan.",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.delete(
            (
                f"/api/conversations/"
                f"{self.conversation.id}/messages/"
                f"{message.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Message.objects.filter(
                id=message.id
            ).exists()
        )
