import threading
import pystray
from PIL import Image
from app.host.notifer import notify
from logging import getLogger

logger = getLogger(__name__)

tray_icon = None
connection_status = "未接続"
register_with_retry = None  # 外部からセットされる

def setup_tray():
    global tray_icon

    def generate_menu():
        return pystray.Menu(
            pystray.MenuItem(f"サーバー接続状態：{connection_status}", None, enabled=False),
            pystray.MenuItem("サーバーに再接続", on_reconnect),
            pystray.MenuItem("スマホで接続", lambda icon, item: notify("スマホで接続するには、QRコードをスキャンしてください。")),
            pystray.MenuItem("終了", on_quit)
        )

    icon = pystray.Icon("RemotePhone", Image.open("app.ico"), menu=generate_menu())
    tray_icon = icon
    return icon

def update_tray():
    if tray_icon:
        tray_icon.menu = pystray.Menu(
            pystray.MenuItem(f"接続状態：{connection_status}", None, enabled=False),
            pystray.MenuItem("サーバーに再接続", on_reconnect),
            pystray.MenuItem("スマホで接続", lambda icon, item: notify("スマホで接続するには、QRコードをスキャンしてください。")),
            pystray.MenuItem("終了", on_quit)
        )
        tray_icon.update_menu()

def on_reconnect(icon, item):
    logger.info("再接続がリクエストされました。")
    notify("サーバーへの再接続を試みます。")

    def reconnect():
        if register_with_retry:
            with threading.Lock():
                register_with_retry()

    threading.Thread(target=reconnect, daemon=True).start()

def on_quit(icon, item):
    logger.info("終了処理が呼ばれました。")
    icon.stop()
