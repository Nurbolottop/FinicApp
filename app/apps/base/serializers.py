from rest_framework import serializers

from apps.base import models as base_models
from apps.accounts import models as accounts_models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Category
        fields = ("id", "name", "slug")


class CampaignImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.CampaignImage
        fields = (
            "id",
            "image",
            "created_at",
        )


class CampaignSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    category = serializers.SlugRelatedField(
        slug_field="slug",
        read_only=True,
    )
    category_slug = serializers.SlugField(source="category.slug", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    images = CampaignImageSerializer(many=True, read_only=True)

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
            "category",
            "category_slug",
            "category_name",
            "image",
            "images",
            "created_at",
        )


class CampaignCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=base_models.Category.objects.all(),
        slug_field="slug",
        required=False,
        allow_null=True,
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = base_models.Campaign
        fields = (
            "title",
            "description",
            "category",
            "goal_amount",
            "end_date",
            "image",
            "images",
        )

    def validate_goal_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цель должна быть больше 0.")
        return value

    def to_internal_value(self, data):
        if hasattr(data, "getlist") and "images" in data:
            images = data.getlist("images")
            if images:
                try:
                    data = data.copy()
                except Exception:
                    data = dict(data)

                if hasattr(data, "setlist"):
                    data.setlist("images", images)
                else:
                    data["images"] = images

        return super().to_internal_value(data)

    def validate_images(self, value):
        if value is None:
            return value
        if len(value) > 10:
            raise serializers.ValidationError("Максимум 10 картинок")
        return value

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        campaign = super().create(validated_data)

        if images:
            if len(images) > 10:
                raise serializers.ValidationError("Максимум 10 картинок")
            base_models.CampaignImage.objects.bulk_create(
                [base_models.CampaignImage(campaign=campaign, image=img) for img in images]
            )

        return campaign

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        instance = super().update(instance, validated_data)

        if images is not None:
            current_count = instance.images.count()
            if current_count + len(images) > 10:
                raise serializers.ValidationError("Максимум 10 картинок")
            base_models.CampaignImage.objects.bulk_create(
                [base_models.CampaignImage(campaign=instance, image=img) for img in images]
            )

        return instance


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


class ReportMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.ReportMedia
        fields = ("id", "file", "media_type", "created_at")


class ReportSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )
    campaign_title = serializers.CharField(
        source="campaign.title",
        read_only=True,
        allow_null=True,
        default=None,
    )
    media_files = ReportMediaSerializer(many=True, read_only=True)

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
            "media_files",
            "created_at",
        )


class ReportCreateSerializer(serializers.ModelSerializer):
    media_files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = base_models.Report
        fields = (
            "title",
            "description",
            "amount_spent",
            "campaign",
            "file",
            "media_files",
        )

    def validate_amount_spent(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше 0.")
        return value

    def validate_media_files(self, files):
        if not files:
            return files

        image_count = 0
        video_count = 0

        for f in files:
            name = f.name.lower()
            if name.endswith((".mp4", ".mov", ".avi", ".mkv")):
                video_count += 1
            else:
                image_count += 1

        if image_count > 4:
            raise serializers.ValidationError("Максимум 4 фото.")
        if video_count > 1:
            raise serializers.ValidationError("Максимум 1 видео.")

        return files

    def create(self, validated_data):
        media_files = validated_data.pop("media_files", [])
        report = super().create(validated_data)

        for media_file in media_files:
            file_name = media_file.name.lower()
            if file_name.endswith((".mp4", ".mov", ".avi", ".mkv")):
                media_type = base_models.ReportMedia.MediaType.VIDEO
            else:
                media_type = base_models.ReportMedia.MediaType.IMAGE

            base_models.ReportMedia.objects.create(
                report=report,
                file=media_file,
                media_type=media_type,
            )
        return report


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


class HadithSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.Hadith
        fields = ("id", "text", "source", "created_at")


class FCMDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.FCMDeviceToken
        fields = ("token", "device_type")


class FCMDeviceTokenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.FCMDeviceToken
        fields = ("token", "device_type")

    def create(self, validated_data):
        user = self.context["request"].user
        token = validated_data["token"]

        # Update or create token (prevent duplicates)
        device_token, created = base_models.FCMDeviceToken.objects.update_or_create(
            token=token,
            defaults={
                "user": user,
                "device_type": validated_data.get("device_type", "android"),
                "is_active": True,
            },
        )
        return device_token


class ContentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.ContentReport
        fields = ("id", "user", "content_type", "content_id", "reason", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate_content_type(self, value):
        if value not in ["campaign", "organization"]:
            raise serializers.ValidationError("Invalid content type.")
        return value

    def validate(self, attrs):
        content_type = attrs.get("content_type")
        content_id = attrs.get("content_id")

        # Verify that the content exists
        if content_type == "campaign":
            if not base_models.Campaign.objects.filter(id=content_id).exists():
                raise serializers.ValidationError("Campaign does not exist.")
        elif content_type == "organization":
            from apps.accounts.models import Organization
            if not Organization.objects.filter(id=content_id).exists():
                raise serializers.ValidationError("Organization does not exist.")

        return attrs
