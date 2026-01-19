import random
from django.conf import settings

from apps.accounts.models import OTPCode
from apps.accounts.services.whatsapp import WhatsAppService


def generate_otp_code() -> str:
    return str(random.randint(1000, 9999))


def send_otp(phone: str, purpose: str) -> bool:
    """
    Создаёт OTPCode и отправляет его через WhatsApp.
    purpose: "register" или "login"
    """
    code = generate_otp_code()

    OTPCode.objects.create(
        phone=phone,
        code=code,
        purpose=purpose,
    )

    template = getattr(settings, "OTP_MESSAGE_TEMPLATE", "Ваш код подтверждения Finic: {code}")
    message = template.format(code=code)

    # Пока используем только WhatsApp через Green API
    provider = getattr(settings, "WHATSAPP_PROVIDER", "green_api")
    if provider == "green_api":
        return WhatsAppService.send_message(phone, message)

    return False
