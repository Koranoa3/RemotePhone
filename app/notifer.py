
from plyer import notification

def notify(message, title="RemotePhone", duration=5, app_name="RemotePhone"):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=duration,
            app_icon="app.ico"
        )
    except Exception as e:
        print(f"通知送信エラー: {e}")