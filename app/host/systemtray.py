import threading
from logging import getLogger

import pystray
from PIL import Image
from app.host.notifer import notify, NotificationCategory
from app.host.window import start_webview_process, stop_webview_process

logger = getLogger(__name__)

tray_icon = None
connection_status = "Not connected"
register_with_retry = None  # Set externally


def run_tray():
    global tray_icon
    tray_icon = pystray.Icon("RemotePhone", Image.open("app.ico"), menu=_generate_menu())
    try:
        tray_icon.run()
    except Exception as e:
        logger.exception(f"Error occurred in system tray: {e}")
    finally:
        stop_webview_process()
        logger.info("System tray icon stopped.")

def update_tray(connection_status_text:str=None):
    global connection_status
    if connection_status_text:
        connection_status = connection_status_text
    if tray_icon:
        tray_icon.menu = _generate_menu()
        tray_icon.update_menu()


def _generate_menu():
    return pystray.Menu(
        pystray.MenuItem(f"Server: {connection_status}", None, enabled=False),
        pystray.MenuItem("Open Window", start_webview_process, default=True),
        pystray.MenuItem("Reconnect", _on_reconnect),
        pystray.MenuItem("Quit", _on_quit)
    )


def _on_reconnect(icon, item):
    logger.info("Reconnect requested.")
    notify(NotificationCategory.ON_APP_ANOMALY, "Attempting to restart the connection.")

    threading.Thread(target=_do_reconnect, daemon=True).start()


def _do_reconnect():
    if register_with_retry:
        with threading.Lock():
            register_with_retry()


def _on_quit(icon, item):
    logger.info("Quit process called.")
    icon.stop()
