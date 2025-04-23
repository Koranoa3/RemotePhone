from server.register import register, get_local_ip
from server.heartbeat import start_heartbeat
from client.websocket_server import run_websocket_server
import threading, asyncio
import time
import json
from logging import getLogger, config

from PIL import Image

from notifer import notify

logger = getLogger(__name__)

with open('log_config.json', 'r') as f:
    log_conf = json.load(f)

config.dictConfig(log_conf)

def start_heartbeat_thread(server_url, local_ip):
    t = threading.Thread(target=start_heartbeat, args=(server_url, local_ip), daemon=True)
    t.start()

def start_websocket_thread(local_ip):
    threading.Thread(target=lambda: asyncio.run(run_websocket_server(local_ip=local_ip)), daemon=True).start()

def on_quit(icon, item):
    logger.info("終了処理が呼ばれました。")
    icon.stop()
    # exit(0)

import pystray
from pystray import Icon
def setup_tray():
    icon = Icon(
        "RemotePhone",
        Image.open("icon.ico"),
        menu=pystray.Menu(
            pystray.MenuItem("終了", on_quit)
        )
    )
    return icon

SERVER_URL = "http://skyboxx.tplinkdns.com:8000"

def main():
    logger.info("アプリケーションが起動しました。")
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
