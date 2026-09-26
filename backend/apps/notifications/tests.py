from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Notification
from .services import create_notification


class NotificationAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="client_test",
            email="client.test@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.other_user = User.objects.create_user(
            username="other_client",
            email="other.client@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.notification = Notification.objects.create(
            destinataire=self.user,
            type=Notification.Type.NOUVEAU_MESSAGE,
            titre="Nouveau message",
            message="Vous avez reçu un nouveau message.",
            lien="/conversations/1",
        )

        self.other_notification = Notification.objects.create(
            destinataire=self.other_user,
            type=Notification.Type.NOUVELLE_PROPOSITION,
            titre="Nouvelle proposition",
            message="Vous avez reçu une proposition.",
            lien="/demandes/1",
        )

    # --------------------------------------------------
    # LISTE
    # --------------------------------------------------

    def test_authenticated_user_can_list_notifications(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/notifications/"
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
            self.notification.id,
            ids,
        )

    def test_user_only_sees_own_notifications(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/notifications/"
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
            self.notification.id,
            ids,
        )

        self.assertNotIn(
            self.other_notification.id,
            ids,
        )

    def test_unauthenticated_user_cannot_list_notifications(self):
        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------
    # VALEURS PAR DÉFAUT
    # --------------------------------------------------

    def test_notification_is_unread_by_default(self):
        notification = Notification.objects.create(
            destinataire=self.user,
            type=Notification.Type.NOUVEL_AVIS,
            titre="Nouvel avis",
            message="Vous avez reçu un nouvel avis.",
        )

        self.assertFalse(
            notification.is_read
        )

        self.assertIsNone(
            notification.read_at
        )

    # --------------------------------------------------
    # SERVICE create_notification
    # --------------------------------------------------

    def test_create_notification_service(self):
        notification = create_notification(
            destinataire=self.user,
            type_notification=(
                Notification.Type.PROPOSITION_ACCEPTEE
            ),
            titre="Proposition acceptée",
            message=(
                "Votre proposition a été acceptée."
            ),
            lien="/conversations/1",
        )

        self.assertIsNotNone(
            notification.id
        )

        self.assertEqual(
            notification.destinataire,
            self.user,
        )

        self.assertEqual(
            notification.type,
            Notification.Type.PROPOSITION_ACCEPTEE,
        )

        self.assertEqual(
            notification.titre,
            "Proposition acceptée",
        )

        self.assertFalse(
            notification.is_read
        )

    # --------------------------------------------------
    # MARQUER UNE NOTIFICATION COMME LUE
    # --------------------------------------------------

    def test_user_can_mark_notification_as_read(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.notification.id}/marquer-lue/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

    def test_mark_as_read_sets_read_at(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.notification.id}/marquer-lue/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

        self.assertIsNotNone(
            self.notification.read_at
        )

    def test_user_cannot_mark_other_user_notification_as_read(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.other_notification.id}/marquer-lue/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.other_notification.refresh_from_db()

        self.assertFalse(
            self.other_notification.is_read
        )

        self.assertIsNone(
            self.other_notification.read_at
        )

    # --------------------------------------------------
    # MARQUER TOUTES LES NOTIFICATIONS COMME LUES
    # --------------------------------------------------

    def test_user_can_mark_all_notifications_as_read(self):
        second_notification = Notification.objects.create(
            destinataire=self.user,
            type=Notification.Type.NOUVEL_AVIS,
            titre="Nouvel avis",
            message="Un artisan a reçu un avis.",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/notifications/marquer-toutes-lues/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.notification.refresh_from_db()
        second_notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

        self.assertTrue(
            second_notification.is_read
        )

        self.assertIsNotNone(
            self.notification.read_at
        )

        self.assertIsNotNone(
            second_notification.read_at
        )

    def test_mark_all_does_not_modify_other_user_notifications(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/notifications/marquer-toutes-lues/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.other_notification.refresh_from_db()

        self.assertFalse(
            self.other_notification.is_read
        )

        self.assertIsNone(
            self.other_notification.read_at
        )

    # --------------------------------------------------
    # NOTIFICATIONS NON LUES
    # --------------------------------------------------

    def test_non_lues_returns_only_unread_notifications(self):
        read_notification = Notification.objects.create(
            destinataire=self.user,
            type=Notification.Type.NOUVEL_AVIS,
            titre="Notification déjà lue",
            message="Cette notification est déjà lue.",
            is_read=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/notifications/non-lues/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.notification.id,
            ids,
        )

        self.assertNotIn(
            read_notification.id,
            ids,
        )

        self.assertNotIn(
            self.other_notification.id,
            ids,
        )

    def test_unread_count_changes_after_marking_notification_read(
        self,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        response_before = self.client.get(
            "/api/notifications/non-lues/"
        )

        self.assertEqual(
            response_before.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response_before.data["count"],
            1,
        )

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.notification.id}/marquer-lue/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response_after = self.client.get(
            "/api/notifications/non-lues/"
        )

        self.assertEqual(
            response_after.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response_after.data["count"],
            0,
        )
