from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts import models as accounts_models


@admin.register(accounts_models.User)
class UserAdmin(DjangoUserAdmin):
    model = accounts_models.User
    ordering = ("email",)

    list_display = ("id", "username", "email", "role", "is_active", "is_staff")
    search_fields = ("username", "email", "phone")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )


@admin.register(accounts_models.DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "rank", "impact_points")
    search_fields = ("user__username", "user__email")


@admin.register(accounts_models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "verified_status", "total_raised")
    search_fields = ("name", "user__email")


@admin.register(accounts_models.OrganizationRequest)
class OrganizationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "org_name",
        "full_name",
        "phone",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("org_name", "full_name", "phone", "email")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Контактное лицо", {"fields": ("full_name", "phone", "email")}),
        ("Организация", {"fields": ("org_name",)}),
        ("Статус", {"fields": ("status", "admin_comment", "created_user")}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )
