from rest_framework import serializers

from apps.artisans.serializers import ArtisanSerializer
from apps.demandes.models import DemandeTravaux

from .models import Proposition


class PropositionSerializer(serializers.ModelSerializer):
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
        model = Proposition

        fields = (
            "id",
            "demande_id",
            "demande_titre",
            "artisan",
            "message",
            "prix_propose",
            "date_disponibilite",
            "statut",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "artisan",
            "statut",
            "created_at",
            "updated_at",
        )

    def validate_prix_propose(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Le prix proposé doit être supérieur à zéro."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")
        demande = attrs.get(
            "demande",
            getattr(self.instance, "demande", None),
        )

        if request and not hasattr(
            request.user,
            "artisan_profile",
        ):
            raise serializers.ValidationError(
                "Seul un artisan peut envoyer une proposition."
            )

        if (
            demande
            and demande.statut
            != DemandeTravaux.Statut.PUBLIEE
        ):
            raise serializers.ValidationError(
                "Cette demande n'accepte plus de propositions."
            )

        if (
            request
            and demande
            and demande.client == request.user
        ):
            raise serializers.ValidationError(
                "Vous ne pouvez pas répondre à votre propre demande."
            )

        return attrs
