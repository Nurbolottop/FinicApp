from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
)

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework.response import Response

from apps.base import models as base_models
from apps.base import serializers as base_serializers
from apps.accounts import models as accounts_models
from apps.accounts import serializers as accounts_serializers
from apps.accounts.permissions import IsDonor, IsOrganization


class OrganizationListView(ListModelMixin, GenericAPIView):
    queryset = accounts_models.Organization.objects.all()
    serializer_class = accounts_serializers.OrganizationSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DonorStatsView(GenericAPIView):
    permission_classes = [IsDonor]

    def get(self, request, *args, **kwargs):
        qs = base_models.Donation.objects.filter(
            donor=request.user
        )

        total_amount = qs.aggregate(
            total=Sum("amount")
        )["total"] or 0

        total_donations = qs.count()

        monthly = (
            qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        return Response({
            "total_amount": total_amount,
            "total_donations": total_donations,
            "monthly": list(monthly),
        })


class OrganizationStatsView(GenericAPIView):
    permission_classes = [IsOrganization]

    def get(self, request, *args, **kwargs):
        organization = request.user.organization

        donations_qs = base_models.Donation.objects.filter(
            organization=organization
        )

        total_raised = donations_qs.aggregate(
            total=Sum("amount")
        )["total"] or 0

        donors_count = donations_qs.values("donor").distinct().count()
        campaigns_count = base_models.Campaign.objects.filter(
            organization=organization
        ).count()

        monthly = (
            donations_qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        return Response({
            "total_raised": total_raised,
            "donors_count": donors_count,
            "campaigns_count": campaigns_count,
            "monthly": list(monthly),
        })


class ReportCreateView(CreateModelMixin, GenericAPIView):
    serializer_class = base_serializers.ReportCreateSerializer
    permission_classes = [IsOrganization]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OrganizationReportsView(ListModelMixin, GenericAPIView):
    serializer_class = base_serializers.ReportSerializer
    permission_classes = []  # публичный доступ

    def get_queryset(self):
        org_id = self.kwargs.get("org_id")
        return base_models.Report.objects.filter(
            organization_id=org_id
        ).order_by("-created_at")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrganizationDetailView(RetrieveModelMixin, GenericAPIView):
    queryset = accounts_models.Organization.objects.all()
    serializer_class = accounts_serializers.OrganizationSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CampaignListView(ListModelMixin, GenericAPIView):
    queryset = base_models.Campaign.objects.all()
    serializer_class = base_serializers.CampaignSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DonationCreateView(CreateModelMixin, GenericAPIView):
    serializer_class = base_serializers.DonationCreateSerializer
    permission_classes = [IsDonor]

    def perform_create(self, serializer):
        donation = serializer.save(
            donor=self.request.user,
            status=base_models.Donation.Status.PENDING,
        )

        base_models.Payment.objects.create(
            donor=self.request.user,
            donation=donation,
            amount=donation.amount,
            provider="stub",
            status=base_models.Payment.Status.PENDING,
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PaymentCompleteStubView(GenericAPIView):
    permission_classes = [IsDonor]

    def post(self, request, payment_id, *args, **kwargs):
        payment = base_models.Payment.objects.get(
            id=payment_id,
            donor=request.user,
        )

        payment.status = base_models.Payment.Status.COMPLETED
        payment.save()

        donation = payment.donation
        donation.status = base_models.Donation.Status.COMPLETED
        donation.save()

        return Response({
            "status": "ok",
            "payment_id": payment.id,
            "donation_id": donation.id,
        })


class MyDonationsView(ListModelMixin, GenericAPIView):
    serializer_class = base_serializers.DonationSerializer
    permission_classes = [IsDonor]

    def get_queryset(self):
        return base_models.Donation.objects.filter(
            donor=self.request.user
        ).order_by("-created_at")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CampaignCreateView(CreateModelMixin, GenericAPIView):
    serializer_class = base_serializers.CampaignCreateSerializer
    permission_classes = [IsOrganization]

    def post(self, request, *args, **kwargs):
        """
        Создание кампании организацией.
        organization берётся из request.user.organization.
        """
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class MyCampaignsView(ListModelMixin, GenericAPIView):
    serializer_class = base_serializers.CampaignSerializer
    permission_classes = [IsOrganization]

    def get_queryset(self):
        """
        Возвращает только те кампании, которые принадлежат текущей организации.
        """
        return base_models.Campaign.objects.filter(
            organization=self.request.user.organization
        ).order_by("-created_at")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
