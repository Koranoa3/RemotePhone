from server.register import register, get_local_ip
from server.heartbeat import start_heartbeat
from client.websocket_server import run_websocket_server
import threading, asyncio
import time

import json
from logging import getLogger, config
logger = getLogger(__name__)

with open('log_config.json', 'r') as f:
    log_conf = json.load(f)

config.dictConfig(log_conf)

SERVER_URL = "http://skyboxx.tplinkdns.com:8000"
if __name__ == "__main__":

    success = register(SERVER_URL, port=8765)
    if success:
        local_ip = get_local_ip()
        t = threading.Thread(target=start_heartbeat, args=(SERVER_URL, local_ip), daemon=True)
        t.start()
        logger.info("ホストは登録され、ハートビートを開始しました。")

    else:
        logger.error("ホストの登録に失敗しました。時間をおいてやりなおすか、管理者に連絡してください。")
        exit(1)
    
    asyncio.run(run_websocket_server(local_ip=local_ip))

    try:
        while True:
            time.sleep(1)  # メインスレッド維持
    except KeyboardInterrupt:
        logger.info("終了します。")
        exit(0)