import threading
from logging import getLogger

import pystray
from PIL import Image
from app.host.notifer import notify
from app.host.connect_dialog import show_qrcode_dialog

logger = getLogger(__name__)

root = None  # tkinterのルートウィンドウ
tray_icon = None
connection_status = "未接続"
register_with_retry = None  # 外部からセットされる


def setup_tray():
    global tray_icon
    tray_icon = pystray.Icon("RemotePhone", Image.open("app.ico"), menu=_generate_menu())
    tray_icon.run()
    root.after(0, root.quit)


def update_tray():
    if tray_icon:
        tray_icon.menu = _generate_menu()
        tray_icon.update_menu()


def _generate_menu():
    return pystray.Menu(
        pystray.MenuItem(f"サーバー接続状態：{connection_status}", None, enabled=False),
        pystray.MenuItem("サーバーに再接続", _on_reconnect),
        pystray.MenuItem("スマホで接続", show_qrcode_dialog),
        pystray.MenuItem("終了", _on_quit)
    )


def _on_reconnect(icon, item):
    logger.info("再接続がリクエストされました。")
    notify("サーバーへの再接続を試みます。")

    threading.Thread(target=_do_reconnect, daemon=True).start()


def _do_reconnect():
    if register_with_retry:
        with threading.Lock():
            register_with_retry()


def _on_quit(icon, item):
    logger.info("終了処理が呼ばれました。")
    icon.stop()
