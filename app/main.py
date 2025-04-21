from server.register import register, get_local_ip
from server.heartbeat import start_heartbeat
from client.websocket_server import run_websocket_server
import threading, asyncio
import time

if __name__ == "__main__":
    server_url = "http://skyboxx.tplinkdns.com:8000"

    success = register(server_url, password="password")
    if success:
        local_ip = get_local_ip()
        t = threading.Thread(target=start_heartbeat, args=(server_url, local_ip), daemon=True)
        t.start()
        print("ホストは登録され、ハートビートを開始しました。")

    else:
        print("ホストの登録に失敗しました。時間をおいてやりなおすか、管理者に連絡してください。")
        exit(1)
    
    asyncio.run(run_websocket_server(local_ip=local_ip))

    try:
        while True:
            time.sleep(1)  # メインスレッド維持
    except KeyboardInterrupt:
        print("終了します。")
