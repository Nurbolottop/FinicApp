import random
from django.conf import settings

from apps.accounts.models import OTPCode
from apps.accounts.services.whatsapp import WhatsAppService


# Тестовый номер для App Store review
TEST_PHONE_NUMBER = "+996775232350"
TEST_OTP_CODE = "1234"


def generate_otp_code(phone: str = None) -> str:
    # Для тестового номера всегда возвращаем тестовый код
    if phone and phone.strip() == TEST_PHONE_NUMBER:
        return TEST_OTP_CODE
    return str(random.randint(1000, 9999))


def send_otp(phone: str, purpose: str) -> bool:
    """
    Создаёт OTPCode и отправляет его через WhatsApp.
    purpose: "register" или "login"
    """
    code = generate_otp_code(phone)

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
