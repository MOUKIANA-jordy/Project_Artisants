from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from rest_framework import serializers

from .models import User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "telephone",
            "role",
            "is_verified",
        )
        read_only_fields = (
            "id",
            "is_verified",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "telephone",
            "role",
            "password",
            "password_confirmation",
        )

        read_only_fields = ("id",)

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "Vous ne pouvez pas créer un compte administrateur."
            )

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirmation = attrs.pop(
            "password_confirmation",
            None,
        )

        if password != password_confirmation:
            raise serializers.ValidationError(
                {
                    "password_confirmation": (
                        "Les deux mots de passe ne correspondent pas."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email
        token["username"] = user.username
        token["role"] = user.role
        token["is_verified"] = user.is_verified

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = UserPublicSerializer(
            self.user
        ).data

        return data
