from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        DONOR = "donor", "Донор"
        ORG = "org", "Организация"
        ADMIN = "admin", "Администратор"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.DONOR,
    )

    phone = models.CharField(max_length=30, blank=True, null=True)

    def is_donor(self) -> bool:
        return self.role == self.Roles.DONOR

    def is_org(self) -> bool:
        return self.role == self.Roles.ORG


class DonorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="donor_profile",
    )
    avatar = models.ImageField(upload_to="avatars/donors/", blank=True, null=True)
    notifications_enabled = models.BooleanField(default=True)
    rank = models.CharField(max_length=50, blank=True, default="")
    impact_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Профиль донора: {self.user.username}"


class Organization(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "На проверке"
        VERIFIED = "verified", "Подтверждена"
        REJECTED = "rejected", "Отклонена"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="organization",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="org_logos/", blank=True, null=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    verified_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    total_raised = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return self.name
