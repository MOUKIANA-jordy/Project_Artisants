from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from apps.artisans.serializers import ArtisanSerializer
from apps.demandes.models import DemandeTravaux
from apps.propositions.models import Proposition

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    client = UserPublicSerializer(read_only=True)
    artisan = ArtisanSerializer(read_only=True)

    demande_id = serializers.PrimaryKeyRelatedField(
        queryset=DemandeTravaux.objects.all(),
        source="demande",
        write_only=True,
    )

    demande_titre = serializers.CharField(
        source="demande.titre",
        read_only=True,
    )

    class Meta:
        model = Review

        fields = (
            "id",
            "client",
            "artisan",
            "demande_id",
            "demande_titre",
            "rating",
            "commentaire",
            "is_visible",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "client",
            "artisan",
            "is_visible",
            "created_at",
            "updated_at",
        )

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "La note doit être comprise entre 1 et 5."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")
        demande = attrs.get(
            "demande",
            getattr(self.instance, "demande", None),
        )

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Vous devez être connecté."
            )

        if request.user.role != "client":
            raise serializers.ValidationError(
                "Seul un client peut laisser un avis."
            )

        if demande.client != request.user:
            raise serializers.ValidationError(
                {
                    "demande_id": (
                        "Cette demande ne vous appartient pas."
                    )
                }
            )

        if demande.statut != DemandeTravaux.Statut.TERMINEE:
            raise serializers.ValidationError(
                {
                    "demande_id": (
                        "Les travaux doivent être terminés "
                        "avant de laisser un avis."
                    )
                }
            )

        proposition_acceptee = (
            Proposition.objects
            .filter(
                demande=demande,
                statut=Proposition.Statut.ACCEPTEE,
            )
            .select_related("artisan")
            .first()
        )

        if proposition_acceptee is None:
            raise serializers.ValidationError(
                {
                    "demande_id": (
                        "Aucun artisan accepté n'a été trouvé "
                        "pour cette demande."
                    )
                }
            )

        if (
            not self.instance
            and Review.objects.filter(demande=demande).exists()
        ):
            raise serializers.ValidationError(
                {
                    "demande_id": (
                        "Un avis existe déjà pour cette demande."
                    )
                }
            )

        attrs["artisan"] = proposition_acceptee.artisan

        return attrs
