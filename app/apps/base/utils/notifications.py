from django.conf import settings
from django.core.mail import send_mail

from apps.base.utils.fcm import send_notification_to_user


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


def send_push_notification_to_user(user, title, message, data=None, image_url=None):
    """
    Send FCM push notification to user.
    """
    return send_notification_to_user(
        user=user,
        title=title,
        body=message,
        data=data,
        image_url=image_url,
    )


def create_and_send_notification(user, title, message, data=None, send_push=True):
    """
    Create database notification and optionally send push notification.

    Args:
        user: User to notify
        title: Notification title
        message: Notification message
        data: Additional data for push notification
        send_push: Whether to send FCM push notification

    Returns:
        tuple: (Notification instance, push result dict)
    """
    from apps.base.models import Notification

    # Create database notification
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
    )

    push_result = None
    if send_push:
        push_result = send_push_notification_to_user(
            user=user,
            title=title,
            message=message,
            data=data,
        )

    return notification, push_result
