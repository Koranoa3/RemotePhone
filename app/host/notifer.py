
from plyer import notification

def notify(message, title="RemotePhone", duration=5, app_name="RemotePhone"):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=duration
        )
    except Exception as e:
        print(f"Notification sending error: {e}")