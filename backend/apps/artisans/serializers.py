from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer

from .models import Artisan


class ArtisanSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Artisan
        fields = (
            "id",
            "user",
            "nom_entreprise",
            "description",
            "categories",
            "ville",
            "quartier",
            "adresse",
            "latitude",
            "longitude",
            "experience",
            "verified",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "verified",
            "created_at",
            "updated_at",
        )

class ArtisanCreateUpdateSerializer(serializers.ModelSerializer):
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source="categories",
        many=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Artisan
        fields = (
            "id",
            "nom_entreprise",
            "description",
            "category_ids",
            "ville",
            "quartier",
            "adresse",
            "latitude",
            "longitude",
            "experience",
        )
        read_only_fields = ("id",)

    def validate_experience(self, value):
        if value > 80:
            raise serializers.ValidationError(
                "Le nombre d'années d'expérience semble incorrect."
            )
        return value

    def validate(self, attrs):
        latitude = attrs.get(
            "latitude",
            getattr(self.instance, "latitude", None),
        )
        longitude = attrs.get(
            "longitude",
            getattr(self.instance, "longitude", None),
        )

        if (latitude is None) != (longitude is None):
            raise serializers.ValidationError(
                {
                    "latitude": (
                        "La latitude et la longitude doivent être "
                        "fournies ensemble."
                    ),
                    "longitude": (
                        "La latitude et la longitude doivent être "
                        "fournies ensemble."
                    ),
                }
            )

        return attrs
