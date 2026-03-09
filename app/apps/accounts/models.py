from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


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

    phone = models.CharField(max_length=20, blank=True, null=True)

    full_name = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["phone"],
                condition=Q(phone__isnull=False) & ~Q(phone=""),
                name="uniq_accounts_user_phone_not_null",
            )
        ]

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
    city = models.CharField(max_length=255, blank=True, default="")
    website = models.URLField(blank=True, default="")
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


class OTPCode(models.Model):
    class Purpose(models.TextChoices):
        REGISTER = "register", "Register"
        LOGIN = "login", "Login"

    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self, ttl_minutes: int = 5) -> bool:
        return timezone.now() - self.created_at > timedelta(minutes=ttl_minutes)


class OrganizationRequest(models.Model):
    """Заявка организации на доступ (при логине)"""

    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Одобрена"
        REJECTED = "rejected", "Отклонена"

    # Контактные данные подающего заявку
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")

    # Данные об организации
    org_name = models.CharField(max_length=255, verbose_name="Название организации")

    # Статус и даты
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )

    # Комментарий администратора (при отклонении/одобрении)
    admin_comment = models.TextField(blank=True, verbose_name="Комментарий администратора")

    # Связанный пользователь (если заявка одобрена и создан пользователь)
    created_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="org_request",
        verbose_name="Созданный пользователь",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подачи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заявка организации"
        verbose_name_plural = "Заявки организаций"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.org_name} ({self.full_name}) - {self.get_status_display()}"
