from rest_framework import serializers

from .models import ArtisanImage


class ArtisanImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ArtisanImage
        fields = (
            "id",
            "image",
            "image_url",
            "legende",
            "is_primary",
            "ordre",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "image_url",
            "created_at",
            "updated_at",
        )

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        url = obj.image.url

        if request:
            return request.build_absolute_uri(url)

        return url

    def validate_image(self, image):
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            raise serializers.ValidationError(
                "L’image ne doit pas dépasser 5 Mo."
            )

        allowed_types = (
            "image/jpeg",
            "image/png",
            "image/webp",
        )

        if image.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Formats acceptés : JPG, PNG et WEBP."
            )

        return image
