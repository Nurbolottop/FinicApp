from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts import models as accounts_models
from apps.accounts import serializers as accounts_serializers


class RegisterDonorView(CreateModelMixin, GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.RegisterDonorSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RegisterOrgView(CreateModelMixin, GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.RegisterOrgSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DonorProfileView(RetrieveModelMixin, GenericAPIView):
    serializer_class = accounts_serializers.DonorProfileSerializer

    def get_object(self):
        return accounts_models.DonorProfile.objects.get(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class LoginView(TokenObtainPairView):
    """
    JWT-логин с rate limit через ScopedRateThrottle.
    Scope: 'login' — см. DEFAULT_THROTTLE_RATES.
    """

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
