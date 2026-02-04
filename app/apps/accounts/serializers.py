from django.contrib.auth import get_user_model
from rest_framework import serializers

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

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

    @extend_schema_field(OpenApiTypes.OBJECT)
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


class DonorProfileEditSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(
        source="donor_profile.avatar",
        required=False,
        allow_null=True,
    )
    notifications_enabled = serializers.BooleanField(
        source="donor_profile.notifications_enabled",
        required=False,
    )
    rank = serializers.CharField(
        source="donor_profile.rank",
        read_only=True,
    )
    impact_points = serializers.IntegerField(
        source="donor_profile.impact_points",
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "phone",
            "role",
            "avatar",
            "notifications_enabled",
            "rank",
            "impact_points",
        )
        read_only_fields = (
            "id",
            "phone",
            "role",
            "rank",
            "impact_points",
        )

    def update(self, instance, validated_data):
        donor_profile_data = validated_data.pop("donor_profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if donor_profile_data is not None:
            donor_profile, _ = accounts_models.DonorProfile.objects.get_or_create(
                user=instance
            )
            profile_update_fields = []
            if "avatar" in donor_profile_data:
                donor_profile.avatar = donor_profile_data.get("avatar")
                profile_update_fields.append("avatar")
            if "notifications_enabled" in donor_profile_data:
                donor_profile.notifications_enabled = donor_profile_data.get(
                    "notifications_enabled"
                )
                profile_update_fields.append("notifications_enabled")

            if profile_update_fields:
                donor_profile.save(update_fields=profile_update_fields)

        return instance


class OrganizationProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = accounts_models.Organization
        fields = ("name", "description", "city", "website", "logo", "email", "phone")
