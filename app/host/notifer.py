
from plyer import notification
from enum import Enum

from app.host.host_config import load as load_host_config

from logging import getLogger
logger = getLogger(__name__)

class NotificationCategory(Enum):
    ON_APP_ANOMALY = "on_app_anomaly"
    ON_AUTH = "on_auth"
    ON_CONNECT = "on_connect"
    ON_DISCONNECT = "on_disconnect"

def _is_notification_type_enabled(type: NotificationCategory) -> bool:
    """
    Check if a specific notification type is enabled in the host configuration.
    """
    notification_config = load_host_config().get("notification", {})
    if not notification_config.get("enable_desktop_notification", False):
        logger.debug("Desktop notifications are disabled in the configuration.")
        return False

    key_mapping = {
        NotificationCategory.ON_APP_ANOMALY: "notify_application_error",
        NotificationCategory.ON_CONNECT: "notify_device_connect",
        NotificationCategory.ON_DISCONNECT: "notify_device_disconnect",
        NotificationCategory.ON_AUTH: "notify_authentication_request",
    }
    key = key_mapping.get(type)
    if key is None:
        logger.debug(f"No config key mapping for notification type: {type}")
        return False
    return notification_config.get(key, False)


def notify(type: NotificationCategory, message:str, title="RemotePhone", duration=5, app_name="RemotePhone"):
    
    try:
        if not isinstance(type, NotificationCategory):
            raise ValueError("Type must be an instance of NotificationCategory Enum")
        
        if not _is_notification_type_enabled(type):
            logger.debug(f"Notification of type {type} is not enabled, skipping.")
            return
    except Exception as e:
        logger.error(f"Error checking notification type: {e}")
        return
    
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=duration
        )
    except Exception as e:
        logger.exception(f"Notification sending error: {e}")