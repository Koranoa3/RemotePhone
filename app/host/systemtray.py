import threading
from logging import getLogger

import pystray
from PIL import Image
from app.host.notifer import notify
from app.host.connect_dialog import show_qrcode_dialog

logger = getLogger(__name__)

root = None  # tkinter root window
tray_icon = None
connection_status = "Not connected"
register_with_retry = None  # Set externally


def setup_tray():
    global tray_icon
    tray_icon = pystray.Icon("RemotePhone", Image.open("app.ico"), menu=_generate_menu())
    tray_icon.run()
    root.after(0, root.quit)


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
        pystray.MenuItem("Reconnect", _on_reconnect),
        pystray.MenuItem("Connect with phone", show_qrcode_dialog),
        pystray.MenuItem("Quit", _on_quit)
    )


def _on_reconnect(icon, item):
    logger.info("Reconnect requested.")
    notify("Attempting to reconnect to the server.")

    threading.Thread(target=_do_reconnect, daemon=True).start()


def _do_reconnect():
    if register_with_retry:
        with threading.Lock():
            register_with_retry()


def _on_quit(icon, item):
    logger.info("Quit process called.")
    icon.stop()
