from django.contrib import admin

from apps.base import models as base_models


@admin.register(base_models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")


@admin.register(base_models.Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organization", "status", "goal_amount", "raised_amount")
    search_fields = ("title", "organization__name")
    list_filter = ("status",)


@admin.register(base_models.Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("id", "donor", "organization", "campaign", "amount", "status", "created_at")
    search_fields = ("donor__username", "donor__email", "organization__name")
    list_filter = ("status", "created_at")
