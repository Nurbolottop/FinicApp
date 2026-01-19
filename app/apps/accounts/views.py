import random

from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import OpenApiExample, extend_schema

from apps.accounts import models as accounts_models
from apps.accounts import serializers as accounts_serializers
from apps.accounts.services.otp import send_otp


User = get_user_model()


def _normalize_phone(phone: str) -> str:
    return (phone or "").strip()


def _generate_otp_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class DonorRegisterView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.DonorRegisterSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_send"

    @extend_schema(
        tags=["Auth"],
        summary="Register donor (OTP)",
        description="Создаёт донора и отправляет OTP-код для подтверждения.",
        examples=[
            OpenApiExample(
                "Request",
                value={"phone": "+996700123456", "full_name": "Иванов Иван Иванович"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = _normalize_phone(serializer.validated_data["phone"])
        full_name = serializer.validated_data["full_name"].strip()

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "role": User.Roles.DONOR,
                "full_name": full_name,
                "is_active": False,
                "username": f"donor_{phone}",
            },
        )

        if not user.is_donor():
            return Response({"detail": "User with this phone is not a donor."}, status=400)

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
            accounts_models.DonorProfile.objects.get_or_create(user=user)
        else:
            if full_name and user.full_name != full_name:
                user.full_name = full_name
                user.save(update_fields=["full_name"])

        accounts_models.OTPCode.objects.filter(
            phone=phone,
            purpose=accounts_models.OTPCode.Purpose.REGISTER,
        ).delete()

        send_otp(phone, purpose=accounts_models.OTPCode.Purpose.REGISTER)
        return Response({"status": "otp_sent"})


class DonorVerifyView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.PhoneOTPVerifySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

    @extend_schema(
        tags=["Auth"],
        summary="Verify donor registration (OTP)",
        description="Подтверждает регистрацию донора по OTP и возвращает JWT.",
        examples=[
            OpenApiExample(
                "Request",
                value={"phone": "+996700123456", "code": "482931"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = _normalize_phone(serializer.validated_data["phone"])
        code = serializer.validated_data["code"].strip()

        try:
            otp = accounts_models.OTPCode.objects.get(
                phone=phone,
                purpose=accounts_models.OTPCode.Purpose.REGISTER,
            )
        except accounts_models.OTPCode.DoesNotExist:
            return Response({"detail": "OTP not found."}, status=400)

        if otp.is_expired():
            otp.delete()
            return Response({"detail": "OTP expired."}, status=400)

        if otp.code != code:
            return Response({"detail": "Invalid OTP."}, status=400)

        user = User.objects.filter(phone=phone, role=User.Roles.DONOR).first()
        if not user:
            otp.delete()
            return Response({"detail": "Donor not found."}, status=400)

        user.is_active = True
        user.save(update_fields=["is_active"])
        otp.delete()

        return Response(_issue_tokens(user))


class DonorLoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.DonorLoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_send"

    @extend_schema(
        tags=["Auth"],
        summary="Login donor (request OTP)",
        description="Запрашивает OTP для входа донору.",
        examples=[
            OpenApiExample(
                "Request",
                value={"phone": "+996700123456"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = _normalize_phone(serializer.validated_data["phone"])

        user = User.objects.filter(phone=phone, role=User.Roles.DONOR).first()
        if not user:
            return Response({"detail": "Donor not found."}, status=400)

        accounts_models.OTPCode.objects.filter(
            phone=phone,
            purpose=accounts_models.OTPCode.Purpose.LOGIN,
        ).delete()

        send_otp(phone, purpose=accounts_models.OTPCode.Purpose.LOGIN)
        return Response({"status": "otp_sent"})


class DonorLoginVerifyView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.PhoneOTPVerifySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

    @extend_schema(
        tags=["Auth"],
        summary="Verify donor login (OTP)",
        description="Подтверждает вход донора по OTP и возвращает JWT.",
        examples=[
            OpenApiExample(
                "Request",
                value={"phone": "+996700123456", "code": "384920"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = _normalize_phone(serializer.validated_data["phone"])
        code = serializer.validated_data["code"].strip()

        try:
            otp = accounts_models.OTPCode.objects.get(
                phone=phone,
                purpose=accounts_models.OTPCode.Purpose.LOGIN,
            )
        except accounts_models.OTPCode.DoesNotExist:
            return Response({"detail": "OTP not found."}, status=400)

        if otp.is_expired():
            otp.delete()
            return Response({"detail": "OTP expired."}, status=400)

        if otp.code != code:
            return Response({"detail": "Invalid OTP."}, status=400)

        user = User.objects.filter(phone=phone, role=User.Roles.DONOR).first()
        if not user:
            otp.delete()
            return Response({"detail": "Donor not found."}, status=400)

        if not user.is_active:
            return Response({"detail": "User is not active."}, status=400)

        otp.delete()
        return Response(_issue_tokens(user))


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


class OrgLoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = accounts_serializers.OrgLoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    @extend_schema(
        tags=["Auth"],
        summary="Login organization (phone+password)",
        description="Вход организации по телефону и паролю. Возвращает JWT.",
        examples=[
            OpenApiExample(
                "Request",
                value={"phone": "+996555000111", "password": "OrgTempPass123"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = _normalize_phone(serializer.validated_data["phone"])
        password = serializer.validated_data["password"]

        user = User.objects.filter(phone=phone, role=User.Roles.ORG).first()
        if not user:
            return Response({"detail": "Organization user not found."}, status=400)

        # authenticate expects username by default; but password check can be done via user.check_password
        if not user.check_password(password):
            return Response({"detail": "Invalid credentials."}, status=400)

        if not user.is_active:
            return Response({"detail": "User is not active."}, status=400)

        return Response(_issue_tokens(user))
