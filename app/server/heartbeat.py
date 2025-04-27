import time
import requests

from logging import getLogger
logger = getLogger(__name__)

def start_heartbeat(server_url: str, local_ip: str):
    while True:
        try:
            res = requests.post(f"{server_url}/api/heartbeat", json={"local_ip": local_ip})
            # logger.info(f"ハートビート送信: {res.status_code}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"サーバーハートビート失敗: {type(e.__cause__)}")
        except Exception as e:
            logger.warning("サーバーハートビート失敗。サーバーに接続できませんでした")
        time.sleep(60)
