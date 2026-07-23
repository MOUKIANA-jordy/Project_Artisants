from django.utils import timezone
from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer

from .models import DemandeTravaux


class DemandeTravauxSerializer(serializers.ModelSerializer):
    client = UserPublicSerializer(read_only=True)
    categorie = CategorySerializer(read_only=True)

    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source="categorie",
        write_only=True,
    )

    nombre_propositions = serializers.SerializerMethodField()

    class Meta:
        model = DemandeTravaux

        fields = (
            "id",
            "client",
            "categorie",
            "categorie_id",
            "titre",
            "description",
            "ville",
            "quartier",
            "adresse",
            "budget_min",
            "budget_max",
            "date_souhaitee",
            "statut",
            "is_urgent",
            "nombre_propositions",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "client",
            "statut",
            "nombre_propositions",
            "created_at",
            "updated_at",
        )

    def get_nombre_propositions(self, obj):
        return obj.propositions.count()

    def validate_date_souhaitee(self, value):
        if value and value < timezone.localdate():
            raise serializers.ValidationError(
                "La date souhaitée ne peut pas être dans le passé."
            )

        return value

    def validate(self, attrs):
        budget_min = attrs.get(
            "budget_min",
            getattr(self.instance, "budget_min", None),
        )

        budget_max = attrs.get(
            "budget_max",
            getattr(self.instance, "budget_max", None),
        )

        if budget_min is not None and budget_min < 0:
            raise serializers.ValidationError(
                {
                    "budget_min": (
                        "Le budget minimum ne peut pas être négatif."
                    )
                }
            )

        if budget_max is not None and budget_max < 0:
            raise serializers.ValidationError(
                {
                    "budget_max": (
                        "Le budget maximum ne peut pas être négatif."
                    )
                }
            )

        if (
            budget_min is not None
            and budget_max is not None
            and budget_min > budget_max
        ):
            raise serializers.ValidationError(
                {
                    "budget_max": (
                        "Le budget maximum doit être supérieur "
                        "ou égal au budget minimum."
                    )
                }
            )

        return attrs
