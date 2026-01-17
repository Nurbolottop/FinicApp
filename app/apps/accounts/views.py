from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import OpenApiExample, extend_schema

from apps.accounts import models as accounts_models
from apps.accounts import serializers as accounts_serializers


class RegisterDonorView(CreateModelMixin, GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.RegisterDonorSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Register donor",
        description="Регистрация пользователя-донора.",
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "username": "donor1",
                    "email": "donor1@finic.test",
                    "password": "password123",
                    "phone": "+996700000001",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RegisterOrgView(CreateModelMixin, GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.RegisterOrgSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Register organization",
        description="Регистрация пользователя-организации (создаётся Organization).",
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "username": "org1",
                    "email": "org1@finic.test",
                    "password": "password123",
                    "phone": "+996700000010",
                    "org_name": "Фонд Добра",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DonorProfileView(RetrieveModelMixin, GenericAPIView):
    serializer_class = accounts_serializers.DonorProfileSerializer

    def get_object(self):
        return accounts_models.DonorProfile.objects.get(user=self.request.user)

    @extend_schema(
        tags=["Me"],
        summary="Get my donor profile",
        description="Возвращает профиль текущего донора. Требуется JWT access token.",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class LoginView(TokenObtainPairView):
    """
    JWT-логин с rate limit через ScopedRateThrottle.
    Scope: 'login' — см. DEFAULT_THROTTLE_RATES.
    """

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


LoginView = extend_schema(
    tags=["Auth"],
    summary="Login (JWT)",
    description=(
        "JWT логин. Возвращает `access` и `refresh`. "
        "Используй `Authorization: Bearer <access>` для защищённых запросов."
    ),
    examples=[
        OpenApiExample(
            "Request",
            value={"email": "donor1@finic.test", "password": "password123"},
            request_only=True,
        ),
        OpenApiExample(
            "Response",
            value={"refresh": "<jwt>", "access": "<jwt>"},
            response_only=True,
        ),
    ],
)(LoginView)
