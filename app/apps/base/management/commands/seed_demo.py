import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.accounts import models as accounts_models
from apps.base import models as base_models


PASSWORD = "12345678"


class Command(BaseCommand):
    help = "Seed demo data for Finic (ALL models + test users)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-demo",
            action="store_true",
            help="Delete demo data (users *@finic.test and related base objects) before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Seeding demo data..."))

        if options.get("clear_demo"):
            demo_users = accounts_models.User.objects.filter(email__endswith="@finic.test")
            base_models.Donation.objects.filter(donor__in=demo_users).delete()
            base_models.Payment.objects.filter(donor__in=demo_users).delete()
            base_models.Notification.objects.filter(user__in=demo_users).delete()
            base_models.Report.objects.filter(organization__user__in=demo_users).delete()
            base_models.Campaign.objects.filter(organization__user__in=demo_users).delete()
            accounts_models.Organization.objects.filter(user__in=demo_users).delete()
            accounts_models.DonorProfile.objects.filter(user__in=demo_users).delete()
            demo_users.delete()

        # --------------------------------------------------
        # USERS (DONORS)
        # --------------------------------------------------
        donors = []
        for i in range(1, 6):
            email = f"donor{i}@finic.test"
            username = f"donor{i}"
            user, _ = accounts_models.User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "role": "donor",
                    "is_active": True,
                },
            )
            user.set_password(PASSWORD)
            user.save()
            donors.append(user)

            accounts_models.DonorProfile.objects.get_or_create(user=user)

        # --------------------------------------------------
        # USERS (ORGANIZATIONS)
        # --------------------------------------------------
        org_users = []
        for i in range(1, 4):
            email = f"org{i}@finic.test"
            username = f"org{i}"
            user, _ = accounts_models.User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "role": "org",
                    "is_active": True,
                },
            )
            user.set_password(PASSWORD)
            user.save()
            org_users.append(user)

        # --------------------------------------------------
        # ORGANIZATIONS
        # --------------------------------------------------
        organizations = []
        for idx, user in enumerate(org_users, start=1):
            org, _ = accounts_models.Organization.objects.get_or_create(
                user=user,
                defaults={
                    "name": f"Organization {idx}",
                    "description": f"Demo organization #{idx}",
                },
            )
            organizations.append(org)

        # --------------------------------------------------
        # CATEGORIES
        # --------------------------------------------------
        category_names = [
            "Медицина",
            "Образование",
            "Дети",
            "Экология",
            "Животные",
        ]
        categories = []
        for name in category_names:
            category, _ = base_models.Category.objects.get_or_create(
                slug=slugify(name, allow_unicode=True),
                defaults={"name": name},
            )
            categories.append(category)

        # --------------------------------------------------
        # CAMPAIGNS
        # --------------------------------------------------
        campaigns = []
        for i in range(1, 6):
            org = random.choice(organizations)
            campaign, _ = base_models.Campaign.objects.get_or_create(
                organization=org,
                title=f"Campaign {i} ({org.name})",
                defaults={
                    "description": f"Demo campaign description #{i}",
                    "goal_amount": Decimal(random.randint(100_000, 800_000)),
                    "status": base_models.Campaign.Status.ACTIVE,
                },
            )
            campaigns.append(campaign)

        # --------------------------------------------------
        # DONATIONS + PAYMENTS (COMPLETED)
        # --------------------------------------------------
        for _ in range(25):
            donor = random.choice(donors)
            org = random.choice(organizations)
            org_campaigns = [c for c in campaigns if c.organization_id == org.id]
            campaign = random.choice(org_campaigns) if org_campaigns else None
            category = random.choice(categories)

            amount = Decimal(random.choice([500, 1000, 1500, 2000, 5000, 10000]))

            donation = base_models.Donation.objects.create(
                donor=donor,
                organization=org,
                campaign=campaign,
                category=category,
                amount=amount,
                status=base_models.Donation.Status.COMPLETED,
            )

            base_models.Payment.objects.get_or_create(
                donation=donation,
                defaults={
                    "donor": donor,
                    "amount": amount,
                    "provider": "stub",
                    "status": base_models.Payment.Status.COMPLETED,
                },
            )

            # update campaign stats
            campaign.raised_amount = (campaign.raised_amount or 0) + amount
            campaign.donors_count = (
                base_models.Donation.objects.filter(campaign=campaign)
                .values("donor")
                .distinct()
                .count()
            )
            campaign.save()

            org.total_raised = (org.total_raised or 0) + amount
            org.save()

        # --------------------------------------------------
        # REPORTS
        # --------------------------------------------------
        for i in range(1, 6):
            org = random.choice(organizations)
            org_campaigns = [c for c in campaigns if c.organization_id == org.id]
            campaign = random.choice(org_campaigns) if org_campaigns else None
            base_models.Report.objects.get_or_create(
                organization=org,
                campaign=campaign,
                title=f"Report #{i}",
                defaults={
                    "description": "Demo report: funds spent for project needs.",
                    "amount_spent": Decimal(random.randint(10_000, 200_000)),
                },
            )

        # --------------------------------------------------
        # NOTIFICATIONS
        # --------------------------------------------------
        for donor in donors:
            base_models.Notification.objects.get_or_create(
                user=donor,
                title="Добро пожаловать!",
                defaults={
                    "message": "Это тестовое уведомление для донора.",
                },
            )

        for org in organizations:
            base_models.Notification.objects.get_or_create(
                user=org.user,
                title="Добро пожаловать!",
                defaults={
                    "message": "Это тестовое уведомление для организации.",
                },
            )

        # --------------------------------------------------
        # DONE
        # --------------------------------------------------
        self.stdout.write(self.style.SUCCESS("✅ Demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("🔐 Password for ALL users: 12345678"))
        self.stdout.write(self.style.SUCCESS("👤 Donors: donor1@finic.test ... donor5@finic.test"))
        self.stdout.write(self.style.SUCCESS("🏢 Orgs: org1@finic.test ... org3@finic.test"))
