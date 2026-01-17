from rest_framework import serializers

from apps.base import models as base_models
from apps.accounts import models as accounts_models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Category
        fields = ("id", "name", "slug")


class CampaignSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = base_models.Campaign
        fields = (
            "id",
            "title",
            "description",
            "goal_amount",
            "raised_amount",
            "donors_count",
            "status",
            "start_date",
            "end_date",
            "organization",
            "organization_name",
            "created_at",
        )


class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Campaign
        fields = ("title", "description", "goal_amount", "end_date")

    def validate_goal_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цель должна быть больше 0.")
        return value


class DonationCreateSerializer(serializers.ModelSerializer):
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=accounts_models.Organization.objects.all(),
        source="organization",
        write_only=True,
    )
    campaign_id = serializers.PrimaryKeyRelatedField(
        queryset=base_models.Campaign.objects.all(),
        source="campaign",
        write_only=True,
        required=False,
        allow_null=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=base_models.Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = base_models.Donation
        fields = ("id", "amount", "organization_id", "campaign_id", "category_id")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше 0.")
        return value


class DonationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    campaign_title = serializers.CharField(source="campaign.title", read_only=True)

    class Meta:
        model = base_models.Donation
        fields = (
            "id",
            "amount",
            "status",
            "organization",
            "organization_name",
            "campaign",
            "campaign_title",
            "created_at",
        )
