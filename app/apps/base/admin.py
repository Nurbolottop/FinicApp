from django.contrib import admin

from apps.base import models as base_models


@admin.register(base_models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")


@admin.register(base_models.Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "organization",
        "category",
        "status",
        "goal_amount",
        "raised_amount",
        "image",
    )
    search_fields = ("title", "organization__name")
    list_filter = ("status", "category")


@admin.register(base_models.CampaignImage)
class CampaignImageAdmin(admin.ModelAdmin):
    list_display = ("id", "campaign", "image", "created_at")
    search_fields = ("campaign__title",)


@admin.register(base_models.Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("id", "donor", "organization", "campaign", "amount", "status", "created_at")
    search_fields = ("donor__username", "donor__email", "organization__name")
    list_filter = ("status", "created_at")


@admin.register(base_models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "organization",
        "campaign",
        "amount_spent",
        "created_at",
    )
    search_fields = (
        "title",
        "organization__name",
        "campaign__title",
    )
    list_filter = ("organization",)


@admin.register(base_models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "donor",
        "donation",
        "amount",
        "provider",
        "status",
        "created_at",
    )
    list_filter = ("status", "provider")
    search_fields = ("donor__email",)


@admin.register(base_models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("user__email", "title")


@admin.register(base_models.DonorBankDetails)
class DonorBankDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "donor", "bank_name", "account_number", "created_at")
    search_fields = ("donor__phone", "bank_name", "account_number")
