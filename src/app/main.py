import threading, asyncio
import time, json, sys, os

### logging ###############################

from logging import getLogger, config
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)
with open(resource_path("app/log_config.json"), "r", encoding="utf-8") as f:
    log_conf = json.load(f)
config.dictConfig(log_conf)
logger = getLogger(__name__)
logger.info("初期化中...")

from app.notifer import notify

### core process thread ###############################

heartbeat_thread = None
def start_heartbeat_thread(server_url, local_ip):
    global heartbeat_thread

    if heartbeat_thread and heartbeat_thread.is_alive():
        logger.info("ハートビートスレッドは既に起動中です。")
        return

    from app.server.heartbeat import start_heartbeat
    heartbeat_thread = threading.Thread(target=start_heartbeat, args=(server_url, local_ip), daemon=True)
    heartbeat_thread.start()

def start_websocket_thread(local_ip):
    from app.client.websocket_server import run_websocket_server
    threading.Thread(target=lambda: asyncio.run(run_websocket_server(local_ip=local_ip)), daemon=True).start()

register_lock = threading.Lock()
def register_with_retry():
    global connection_status

    from app.server.register import register, get_local_ip

    connection_status = "接続中"
    update_tray()

    attempts = 1
    while attempts < 10:
        success = register(SERVER_URL, port=8765)
        if success:
            local_ip = get_local_ip()
            start_heartbeat_thread(SERVER_URL, local_ip)
            start_websocket_thread(local_ip)
            connection_status = "接続済み"
            update_tray()
            logger.info("ホストは登録され、ハートビートとWebSocketサーバーを開始しました。")
            return
        else:
            retry_after = attempts ** 2 + 5
            notify(f"登録に失敗しました。{retry_after}秒後に再試行します。")
            logger.info(f"登録に失敗しました。{retry_after}秒後に再試行します。")
            time.sleep(retry_after)
            attempts += 1

    connection_status = "失敗"
    update_tray()
    notify("登録に失敗しました。メニューから手動で再接続してください。")
    logger.error("登録に失敗しました。")


### tray icon ###############################

connection_status = "未接続"
tray_icon = None  # Iconインスタンスを外から参照できるようにする

import pystray
from PIL import Image
def setup_tray():
    global tray_icon

    def generate_menu():
        return pystray.Menu(
            pystray.MenuItem(f"接続状態：{connection_status}", lambda icon, item: None, enabled=False),
            pystray.MenuItem("サーバーに再接続", on_reconnect),
            pystray.MenuItem("終了", on_quit)
        )

    icon = pystray.Icon(
        "RemotePhone",
        Image.open("app.ico"),
        menu=generate_menu()
    )
    tray_icon = icon
    return icon

def update_tray():
    if tray_icon:
        tray_icon.menu = pystray.Menu(
            pystray.MenuItem(f"接続状態：{connection_status}", lambda icon, item: None, enabled=False),
            pystray.MenuItem("サーバーに再接続", on_reconnect),
            pystray.MenuItem("終了", on_quit)
        )
        tray_icon.update_menu()

def on_reconnect(icon, item):
    logger.info("再接続がリクエストされました。")
    notify("サーバーへの再接続を試みます。")

    def reconnect():
        with register_lock:
            register_with_retry()

    threading.Thread(target=reconnect, daemon=True).start()
    
def on_quit(icon, item):
    logger.info("終了処理が呼ばれました。")
    icon.stop()

### main function ###############################

SERVER_URL = "http://skyboxx.tplinkdns.com:8000"

def main():
    logger.info("アプリケーションが起動しました。")

    # まずトレイアイコンを即セットアップ
    icon = setup_tray()

    # 接続処理を別スレッドで開始
    register_thread = threading.Thread(target=register_with_retry, daemon=True)
    register_thread.start()

    # トレイアイコンを動かす
    icon.run()

if __name__ == "__main__":
    main()
