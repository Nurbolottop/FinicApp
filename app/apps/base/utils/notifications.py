from django.conf import settings
from django.core.mail import send_mail


def send_notification_email(subject, message, recipient):
    """
    Email-заглушка. В проде заменить на SendGrid / SMTP.
    """
    if not recipient:
        return

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=True,
    )
