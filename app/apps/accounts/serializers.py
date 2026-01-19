from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts import models as accounts_models


User = get_user_model()


class DonorRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=255)


class PhoneOTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)


class DonorLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class OrgLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)


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
            "full_name": obj.user.full_name,
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
