from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.artisans.models import Artisan
from apps.categories.models import Category
from apps.demandes.models import DemandeTravaux
from apps.notifications.models import Notification
from apps.propositions.models import Proposition

from .models import Review


class ReviewAPITests(APITestCase):

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
        # DEMANDE TERMINÉE
        # --------------------------------------------------

        self.demande = DemandeTravaux.objects.create(
            client=self.client_user,
            categorie=self.category,
            titre="Réparation fuite",
            description="Réparation d'une fuite d'eau.",
            ville="Brazzaville",
            quartier="Bacongo",
            statut=DemandeTravaux.Statut.TERMINEE,
        )

        # --------------------------------------------------
        # PROPOSITION ACCEPTÉE
        # --------------------------------------------------

        self.proposition = Proposition.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            message="Je peux effectuer les travaux.",
            prix_propose=30000,
            statut=Proposition.Statut.ACCEPTEE,
        )

    def review_data(self):
        return {
            "demande_id": self.demande.id,
            "rating": 5,
            "commentaire": (
                "Excellent travail, rapide et professionnel."
            ),
        }

    # --------------------------------------------------
    # CRÉATION
    # --------------------------------------------------

    def test_client_can_create_review_for_completed_job(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        review = Review.objects.get()

        self.assertEqual(
            review.client,
            self.client_user,
        )

        self.assertEqual(
            review.artisan,
            self.artisan,
        )

        self.assertEqual(
            review.demande,
            self.demande,
        )

        self.assertEqual(
            review.rating,
            5,
        )

    def test_artisan_is_automatically_selected_from_accepted_proposition(
        self,
    ):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        review = Review.objects.get()

        self.assertEqual(
            review.artisan,
            self.proposition.artisan,
        )

    # --------------------------------------------------
    # AUTHENTIFICATION / RÔLES
    # --------------------------------------------------

    def test_unauthenticated_user_cannot_create_review(self):
        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_artisan_cannot_create_review(self):
        self.client.force_authenticate(
            user=self.artisan_user
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Review.objects.count(),
            0,
        )

    # --------------------------------------------------
    # PROPRIÉTÉ DE LA DEMANDE
    # --------------------------------------------------

    def test_client_cannot_review_other_clients_demande(self):
        self.client.force_authenticate(
            user=self.other_client
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Review.objects.count(),
            0,
        )

    # --------------------------------------------------
    # DEMANDE NON TERMINÉE
    # --------------------------------------------------

    def test_client_cannot_review_unfinished_job(self):
        self.demande.statut = (
            DemandeTravaux.Statut.EN_COURS
        )
        self.demande.save()

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Review.objects.count(),
            0,
        )

    # --------------------------------------------------
    # PROPOSITION ACCEPTÉE OBLIGATOIRE
    # --------------------------------------------------

    def test_review_requires_accepted_proposition(self):
        self.proposition.statut = (
            Proposition.Statut.REFUSEE
        )
        self.proposition.save()

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Review.objects.count(),
            0,
        )

    # --------------------------------------------------
    # NOTE
    # --------------------------------------------------

    def test_rating_cannot_be_zero(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        data = self.review_data()
        data["rating"] = 0

        response = self.client.post(
            "/api/reviews/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_rating_cannot_be_greater_than_five(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        data = self.review_data()
        data["rating"] = 6

        response = self.client.post(
            "/api/reviews/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # DOUBLON
    # --------------------------------------------------

    def test_client_cannot_create_two_reviews_for_same_demande(
        self,
    ):
        Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=5,
            commentaire="Premier avis",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Review.objects.filter(
                demande=self.demande
            ).count(),
            1,
        )

    # --------------------------------------------------
    # NOTIFICATION
    # --------------------------------------------------

    def test_creating_review_notifies_artisan(self):
        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.post(
            "/api/reviews/",
            self.review_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        notification = Notification.objects.filter(
            destinataire=self.artisan_user,
            type=Notification.Type.NOUVEL_AVIS,
        ).first()

        self.assertIsNotNone(
            notification
        )

    # --------------------------------------------------
    # LECTURE PUBLIQUE
    # --------------------------------------------------

    def test_anonymous_user_can_list_visible_reviews(self):
        review = Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=5,
            commentaire="Très bon travail",
        )

        response = self.client.get(
            "/api/reviews/"
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
            review.id,
            ids,
        )

    def test_anonymous_user_cannot_see_hidden_reviews(self):
        review = Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=5,
            commentaire="Avis caché",
            is_visible=False,
        )

        response = self.client.get(
            "/api/reviews/"
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

        self.assertNotIn(
            review.id,
            ids,
        )

    # --------------------------------------------------
    # MODIFICATION
    # --------------------------------------------------

    def test_owner_can_update_review(self):
        review = Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=4,
            commentaire="Bon travail",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.patch(
            f"/api/reviews/{review.id}/",
            {
                "rating": 5,
                "commentaire": "Excellent travail",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        review.refresh_from_db()

        self.assertEqual(
            review.rating,
            5,
        )

        self.assertEqual(
            review.commentaire,
            "Excellent travail",
        )

    def test_other_client_cannot_update_review(self):
        review = Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=4,
            commentaire="Bon travail",
        )

        self.client.force_authenticate(
            user=self.other_client
        )

        response = self.client.patch(
            f"/api/reviews/{review.id}/",
            {
                "rating": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        review.refresh_from_db()

        self.assertEqual(
            review.rating,
            4,
        )

    # --------------------------------------------------
    # SUPPRESSION = MASQUAGE
    # --------------------------------------------------

    def test_owner_can_hide_review_by_deleting_it(self):
        review = Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=5,
            commentaire="Excellent",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.delete(
            f"/api/reviews/{review.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        review.refresh_from_db()

        self.assertFalse(
            review.is_visible
        )

        self.assertTrue(
            Review.objects.filter(
                id=review.id
            ).exists()
        )

    def test_other_client_cannot_delete_review(self):
        review = Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=5,
            commentaire="Excellent",
        )

        self.client.force_authenticate(
            user=self.other_client
        )

        response = self.client.delete(
            f"/api/reviews/{review.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        review.refresh_from_db()

        self.assertTrue(
            review.is_visible
        )

    # --------------------------------------------------
    # MES AVIS
    # --------------------------------------------------

    def test_mes_avis_returns_only_current_users_reviews(self):
        review = Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=5,
            commentaire="Mon avis",
        )

        self.client.force_authenticate(
            user=self.client_user
        )

        response = self.client.get(
            "/api/reviews/mes-avis/"
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
            review.id,
            ids,
        )

    # --------------------------------------------------
    # STATISTIQUES
    # --------------------------------------------------

    def test_statistics_require_artisan_parameter(self):
        response = self.client.get(
            "/api/reviews/statistiques/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_statistics_return_average_and_count(self):
        second_client = User.objects.create_user(
            username="second_client",
            email="second.client@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        second_demande = DemandeTravaux.objects.create(
            client=second_client,
            categorie=self.category,
            titre="Deuxième intervention",
            description="Deuxième travail",
            ville="Brazzaville",
            statut=DemandeTravaux.Statut.TERMINEE,
        )

        Review.objects.create(
            client=self.client_user,
            artisan=self.artisan,
            demande=self.demande,
            rating=4,
            commentaire="Très bien",
        )

        Review.objects.create(
            client=second_client,
            artisan=self.artisan,
            demande=second_demande,
            rating=5,
            commentaire="Excellent",
        )

        response = self.client.get(
            (
                "/api/reviews/statistiques/"
                f"?artisan={self.artisan.id}"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["nombre_avis"],
            2,
        )

        self.assertEqual(
            response.data["note_moyenne"],
            4.5,
        )
