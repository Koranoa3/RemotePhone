import threading, asyncio
import time, json, sys, os

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

def start_heartbeat_thread(server_url, local_ip):
    from app.server.heartbeat import start_heartbeat
    t = threading.Thread(target=start_heartbeat, args=(server_url, local_ip), daemon=True)
    t.start()

def start_websocket_thread(local_ip):
    from app.client.websocket_server import run_websocket_server
    threading.Thread(target=lambda: asyncio.run(run_websocket_server(local_ip=local_ip)), daemon=True).start()


import pystray
from PIL import Image
def setup_tray():
    icon = pystray.Icon(
        "RemotePhone",
        Image.open("icon.ico"),
        menu=pystray.Menu(
            pystray.MenuItem("終了", on_quit)
        )
    )
    return icon

def on_quit(icon, item):
    logger.info("終了処理が呼ばれました。")
    icon.stop()


SERVER_URL = "http://skyboxx.tplinkdns.com:8000"
VERSION = "0.7.0"

def main():
    logger.info("アプリケーションが起動しました。")

    from app.server.updater import check_for_updates
    check_for_updates(SERVER_URL + "/api/version", VERSION)

    from app.server.register import register, get_local_ip
    success = register(SERVER_URL, port=8765)
    if success:
        local_ip = get_local_ip()
        start_heartbeat_thread(SERVER_URL, local_ip)
        start_websocket_thread(local_ip)
        logger.info("ホストは登録され、ハートビートとWebSocketサーバーを開始しました。")
    else:
        logger.error("ホストの登録に失敗しました。時間をおいてやりなおすか、管理者に連絡してください。")
        notify("登録に失敗しました。終了します。")
        time.sleep(3)
        exit(1)

    icon = setup_tray()
    icon.run()

if __name__ == "__main__":
    main()
