import time
import requests

def start_heartbeat(server_url: str, local_ip: str):
    while True:
        try:
            res = requests.post(f"{server_url}/api/heartbeat", json={"local_ip": local_ip})
            # print("♥️ ハートビート送信:", res.status_code)
        except requests.exceptions.ConnectionError as e:
            print(f"💔 サーバーハートビート失敗: {type(e.__cause__)}")
        except Exception as e:
            print("💔 サーバーハートビート失敗。サーバーに接続できませんでした")
        time.sleep(60)
