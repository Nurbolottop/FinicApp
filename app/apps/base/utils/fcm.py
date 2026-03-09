import os
import logging
from typing import List, Optional

from django.conf import settings
from firebase_admin import credentials, messaging, initialize_app, get_app

logger = logging.getLogger(__name__)

_fcm_app = None


def get_fcm_app():
    """Get or initialize Firebase app."""
    global _fcm_app
    if _fcm_app is not None:
        return _fcm_app

    try:
        _fcm_app = get_app()
    except ValueError:
        # App not initialized
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            # Try to load from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            if all([cred_dict["project_id"], cred_dict["private_key"], cred_dict["client_email"]]):
                cred = credentials.Certificate(cred_dict)
            else:
                logger.warning("Firebase credentials not configured. FCM notifications disabled.")
                return None

        _fcm_app = initialize_app(cred)

    return _fcm_app


def send_push_notification(
    tokens: List[str],
    title: str,
    body: str,
    data: Optional[dict] = None,
    image_url: Optional[str] = None,
) -> dict:
    """
    Send FCM push notification to multiple device tokens.

    Args:
        tokens: List of FCM device tokens
        title: Notification title
        body: Notification body
        data: Additional data payload (optional)
        image_url: Image URL for notification (optional)

    Returns:
        dict with success/failure counts
    """
    app = get_fcm_app()
    if app is None:
        logger.warning("FCM not initialized. Skipping push notification.")
        return {"success": 0, "failure": len(tokens), "error": "FCM not initialized"}

    if not tokens:
        return {"success": 0, "failure": 0}

    # Build notification
    notification = messaging.Notification(
        title=title,
        body=body,
        image=image_url,
    )

    # Build Android config
    android_config = messaging.AndroidConfig(
        priority="high",
        notification=messaging.AndroidNotification(
            sound="default",
            channel_id="default_channel",
        ),
    )

    # Build APNS config for iOS
    apns_config = messaging.APNSConfig(
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                sound="default",
                badge=1,
            )
        )
    )

    # Prepare data
    data_payload = data or {}
    data_payload = {k: str(v) for k, v in data_payload.items()}

    # Send to multiple tokens using multicast
    multicast_message = messaging.MulticastMessage(
        tokens=tokens,
        notification=notification,
        data=data_payload,
        android=android_config,
        apns=apns_config,
    )

    try:
        response = messaging.send_multicast(multicast_message, app=app)

        # Handle invalid tokens
        from apps.base.models import FCMDeviceToken

        for idx, result in enumerate(response.responses):
            if not result.success:
                error = result.exception
                if error and "Registration token" in str(error) and "invalid" in str(error).lower():
                    # Token is invalid, remove it
                    token = tokens[idx]
                    FCMDeviceToken.objects.filter(token=token).delete()
                    logger.info(f"Removed invalid FCM token: {token[:20]}...")

        return {
            "success": response.success_count,
            "failure": response.failure_count,
            "total": len(tokens),
        }

    except Exception as e:
        logger.exception("Failed to send FCM notification")
        return {"success": 0, "failure": len(tokens), "error": str(e)}


def send_notification_to_user(
    user,
    title: str,
    body: str,
    data: Optional[dict] = None,
    image_url: Optional[str] = None,
) -> dict:
    """
    Send push notification to a specific user.
    Gets all active FCM tokens for the user.
    """
    from apps.base.models import FCMDeviceToken

    tokens = list(
        FCMDeviceToken.objects.filter(
            user=user,
            is_active=True,
        ).values_list("token", flat=True)
    )

    if not tokens:
        return {"success": 0, "failure": 0, "message": "No active tokens for user"}

    return send_push_notification(tokens, title, body, data, image_url)
