from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
)

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema

from apps.base import models as base_models
from apps.base import serializers as base_serializers
from apps.accounts import models as accounts_models
from apps.accounts import serializers as accounts_serializers
from apps.accounts.permissions import IsDonor, IsOrganization


class OrganizationListView(ListModelMixin, GenericAPIView):
    queryset = accounts_models.Organization.objects.all()
    serializer_class = accounts_serializers.OrganizationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Public"],
        summary="List organizations",
        description="Список организаций (публичный доступ).",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DonorStatsView(GenericAPIView):
    permission_classes = [IsDonor]
    serializer_class = base_serializers.DonorStatsSerializer

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
    serializer_class = base_serializers.OrganizationStatsSerializer

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

    @extend_schema(
        tags=["Organization"],
        summary="Create report",
        description="Создать отчёт (только организация).",
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

    @extend_schema(
        tags=["Public"],
        summary="Get organization by id",
        description="Детальная информация об организации (публичный доступ).",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CampaignListView(ListModelMixin, GenericAPIView):
    serializer_class = base_serializers.CampaignSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = base_models.Campaign.objects.all()

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        org_id = self.request.query_params.get("organization_id")
        if org_id:
            qs = qs.filter(organization_id=org_id)

        return qs.order_by("-created_at")

    @extend_schema(
        tags=["Public"],
        summary="List campaigns",
        description="Список кампаний (публичный доступ). Поддерживает фильтры.",
        parameters=[
            OpenApiParameter(
                name="status",
                required=False,
                type=str,
                description="Фильтр по статусу кампании (например active/completed).",
            ),
            OpenApiParameter(
                name="organization_id",
                required=False,
                type=int,
                description="Фильтр по организации.",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DonationCreateView(CreateModelMixin, GenericAPIView):
    serializer_class = base_serializers.DonationCreateSerializer
    permission_classes = [IsDonor]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "donation"

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

    @extend_schema(
        tags=["Donor"],
        summary="Create donation",
        description=(
            "Создать донат (только донор). После создания автоматически создаётся Payment (stub)."
        ),
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "amount": 500,
                    "organization_id": 1,
                    "campaign_id": 1,
                    "category_id": 1,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PaymentCompleteStubView(GenericAPIView):
    permission_classes = [IsDonor]
    serializer_class = base_serializers.PaymentCompleteStubSerializer

    @extend_schema(
        tags=["Payments"],
        summary="Complete payment (stub)",
        description=(
            "Заглушка оплаты: переводит Payment и Donation в COMPLETED и создаёт уведомления. "
            "Доступно только донору, который создал платёж."
        ),
        examples=[
            OpenApiExample(
                "Response",
                value={"status": "ok", "payment_id": 10, "donation_id": 15},
                response_only=True,
            ),
        ],
    )
    def post(self, request, payment_id, *args, **kwargs):
        payment = get_object_or_404(
            base_models.Payment,
            id=payment_id,
            donor=request.user,
        )

        if payment.status == base_models.Payment.Status.COMPLETED:
            return Response({
                "status": "already_completed",
                "payment_id": payment.id,
                "donation_id": payment.donation.id,
            })

        payment.status = base_models.Payment.Status.COMPLETED
        payment.save()

        donation = payment.donation
        donation.status = base_models.Donation.Status.COMPLETED
        donation.save()

        base_models.Notification.objects.create(
            user=request.user,
            title="Платёж успешно завершён",
            message=f"Спасибо! Ваш донат на сумму {payment.amount} успешно зачислен.",
        )

        base_models.Notification.objects.create(
            user=donation.organization.user,
            title="Новый донат",
            message=f"Поступил донат на сумму {payment.amount}.",
        )

        return Response({
            "status": "ok",
            "payment_id": payment.id,
            "donation_id": donation.id,
        })


class MyNotificationsView(ListModelMixin, GenericAPIView):
    serializer_class = base_serializers.NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return base_models.Notification.objects.filter(
            user=self.request.user
        )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    get = extend_schema(
        tags=["Notifications"],
        summary="List my notifications",
        description="Список уведомлений текущего пользователя.",
    )(get)


class NotificationReadView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = base_serializers.StatusSerializer

    @extend_schema(
        tags=["Notifications"],
        summary="Mark notification as read",
        description="Пометить уведомление как прочитанное.",
        examples=[
            OpenApiExample(
                "Response",
                value={"status": "ok"},
                response_only=True,
            ),
        ],
    )
    def post(self, request, notification_id, *args, **kwargs):
        notification = get_object_or_404(
            base_models.Notification,
            id=notification_id,
            user=request.user,
        )

        notification.is_read = True
        notification.save()

        return Response({"status": "ok"})


class MyDonationsView(ListModelMixin, GenericAPIView):
    serializer_class = base_serializers.DonationSerializer
    permission_classes = [IsDonor]

    def get_queryset(self):
        return base_models.Donation.objects.filter(
            donor=self.request.user
        ).order_by("-created_at")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    get = extend_schema(
        tags=["Donor"],
        summary="List my donations",
        description="Список донатов текущего донора.",
    )(get)


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
