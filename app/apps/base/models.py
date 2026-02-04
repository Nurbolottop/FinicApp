from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Campaign(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        COMPLETED = "completed", "Завершена"
        PAUSED = "paused", "На паузе"

    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    category = models.ForeignKey(
        "base.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaigns",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()

    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    donors_count = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    image = models.ImageField(
        upload_to="campaigns/",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Кампания"
        verbose_name_plural = "Кампании"

    def __str__(self):
        return f"{self.title}"


class CampaignImage(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="campaigns/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Картинка кампании"
        verbose_name_plural = "Картинки кампании"

    def __str__(self):
        return f"CampaignImage {self.id}"


class Donation(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Завершено"
        PENDING = "pending", "Ожидает"
        FAILED = "failed", "Ошибка"

    donor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="donations",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="donations",
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Пожертвование"
        verbose_name_plural = "Пожертвования"

    def __str__(self):
        return f"{self.donor} -> {self.organization}: {self.amount}"


class Report(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="reports",
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    amount_spent = models.DecimalField(max_digits=12, decimal_places=2)

    file = models.FileField(
        upload_to="reports/",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отчёт"
        verbose_name_plural = "Отчёты"

    def __str__(self):
        return f"{self.title} ({self.organization.name})"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        COMPLETED = "completed", "Завершён"
        FAILED = "failed", "Ошибка"

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    donation = models.OneToOneField(
        Donation,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    provider = models.CharField(
        max_length=50,
        default="stub",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Payment {self.id} — {self.status}"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} — {self.user}"


class DonorBankDetails(models.Model):
    donor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bank_details",
    )
    bank_name = models.CharField(max_length=255, blank=True, default="")
    account_number = models.CharField(max_length=255, blank=True, default="")
    account_holder = models.CharField(max_length=255, blank=True, default="")
    extra_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Банковские реквизиты донора"
        verbose_name_plural = "Банковские реквизиты доноров"

    def __str__(self):
        return f"{self.donor} — {self.bank_name}"


class RecurringDonation(models.Model):
    class Interval(models.TextChoices):
        DAILY = "daily", "Ежедневно"

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurring_donations",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="recurring_donations",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interval = models.CharField(
        max_length=20,
        choices=Interval.choices,
        default=Interval.DAILY,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Регулярный донат"
        verbose_name_plural = "Регулярные донаты"

    def __str__(self):
        return f"{self.donor} -> {self.organization} ({self.amount} {self.interval})"
