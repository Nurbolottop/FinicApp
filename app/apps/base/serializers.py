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
            "image",
            "created_at",
        )


class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Campaign
        fields = ("title", "description", "goal_amount", "end_date", "image")

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


class ReportSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )
    campaign_title = serializers.CharField(
        source="campaign.title",
        read_only=True,
    )

    class Meta:
        model = base_models.Report
        fields = (
            "id",
            "title",
            "description",
            "amount_spent",
            "file",
            "organization",
            "organization_name",
            "campaign",
            "campaign_title",
            "created_at",
        )


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Report
        fields = (
            "title",
            "description",
            "amount_spent",
            "campaign",
            "file",
        )

    def validate_amount_spent(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше 0.")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Payment
        fields = (
            "id",
            "amount",
            "provider",
            "status",
            "created_at",
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Notification
        fields = (
            "id",
            "title",
            "message",
            "is_read",
            "created_at",
        )


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField()


class PaymentCompleteStubSerializer(serializers.Serializer):
    status = serializers.CharField()
    payment_id = serializers.IntegerField()
    donation_id = serializers.IntegerField()


class MonthlyAmountSerializer(serializers.Serializer):
    month = serializers.DateTimeField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class DonorStatsSerializer(serializers.Serializer):
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_donations = serializers.IntegerField()
    monthly = MonthlyAmountSerializer(many=True)


class OrganizationStatsSerializer(serializers.Serializer):
    total_raised = serializers.DecimalField(max_digits=12, decimal_places=2)
    donors_count = serializers.IntegerField()
    campaigns_count = serializers.IntegerField()
    monthly = MonthlyAmountSerializer(many=True)


class DonorBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.DonorBankDetails
        fields = (
            "bank_name",
            "account_number",
            "account_holder",
            "extra_info",
        )


class RecurringDonationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    class Meta:
        model = base_models.RecurringDonation
        fields = (
            "id",
            "organization",
            "organization_name",
            "amount",
            "interval",
            "is_active",
            "created_at",
        )
