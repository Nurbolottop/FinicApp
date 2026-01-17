from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts import models as accounts_models


User = get_user_model()


class RegisterDonorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("username", "email", "password", "phone")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.role = User.Roles.DONOR
        user.set_password(password)
        user.save()
        accounts_models.DonorProfile.objects.create(user=user)
        return user


class RegisterOrgSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    org_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "phone", "org_name")

    def create(self, validated_data):
        org_name = validated_data.pop("org_name")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.role = User.Roles.ORG
        user.set_password(password)
        user.save()

        accounts_models.Organization.objects.create(user=user, name=org_name)
        return user


class DonorProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = accounts_models.DonorProfile
        fields = ("user", "avatar", "notifications_enabled", "rank", "impact_points")

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
            "role": obj.user.role,
            "phone": obj.user.phone,
        }


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = accounts_models.Organization
        fields = (
            "id",
            "name",
            "description",
            "logo",
            "email",
            "phone",
            "verified_status",
            "total_raised",
        )
