from register import register, get_local_ip
from heartbeat import start_heartbeat
import threading
import time

if __name__ == "__main__":
    server_url = "http://r620-dell.tail9d6e9.ts.net:8000"

    success = register(server_url, password="password")
    if success:
        local_ip = get_local_ip()
        t = threading.Thread(target=start_heartbeat, args=(server_url, local_ip), daemon=True)
        t.start()
        print("ホストは登録され、ハートビートを開始しました。")

        try:
            while True:
                time.sleep(1)  # メインスレッド維持
        except KeyboardInterrupt:
            print("終了します。")
