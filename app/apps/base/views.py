from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
)

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
        serializer.save(donor=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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
