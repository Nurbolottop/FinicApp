import requests
from django.conf import settings


class WhatsAppService:
    @staticmethod
    def send_message(phone: str, message: str) -> bool:
        """
        phone: в формате +996700123456
        Используем Green API:
        URL: https://api.green-api.com/waInstance{INSTANCE_ID}/sendMessage/{TOKEN}
        Данные: {"chatId": "<phone_without_plus>@c.us", "message": message}
        """
        if not getattr(settings, "GREEN_API_INSTANCE_ID", None) or not getattr(
            settings, "GREEN_API_TOKEN", None
        ):
            return False

        phone_clean = phone.replace("+", "").replace(" ", "")

        url = (
            f"https://api.green-api.com/waInstance"
            f"{settings.GREEN_API_INSTANCE_ID}"
            f"/sendMessage/"
            f"{settings.GREEN_API_TOKEN}"
        )

        payload = {
            "chatId": f"{phone_clean}@c.us",
            "message": message,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
