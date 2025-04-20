import time
import requests

def start_heartbeat(server_url: str, local_ip: str):
    while True:
        try:
            res = requests.post(f"{server_url}/api/heartbeat", json={"local_ip": local_ip})
            print("ハートビート送信:", res.status_code)
        except Exception as e:
            print("ハートビート失敗:", e)
        time.sleep(60)
