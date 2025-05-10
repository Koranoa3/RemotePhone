import threading, asyncio, tkinter as tk
import time, json, sys


### logging ###############################

from logging import getLogger, config
from app.common import resource_path
with open(resource_path("app/resources/log_config.json"), "r", encoding="utf-8") as f:
    log_conf = json.load(f)
config.dictConfig(log_conf)
logger = getLogger(__name__)
logger.info("Initializing...")

from app.host.notifer import notify

### core process thread ###############################

heartbeat_thread = None
def start_heartbeat_thread(server_url, local_ip):
    global heartbeat_thread

    if heartbeat_thread and heartbeat_thread.is_alive():
        logger.info("Heartbeat thread is already running.")
        return

    from app.server.heartbeat import start_heartbeat
    heartbeat_thread = threading.Thread(target=start_heartbeat, args=(server_url, local_ip), daemon=True)
    heartbeat_thread.start()

def start_websocket_thread(local_ip):
    from app.client.websocket_server import run_websocket_server, stop_websocket_server, stop_event
    
    stop_websocket_server()  # 事前に止める
    threading.Thread(target=lambda: asyncio.run(run_websocket_server(local_ip)), daemon=True).start()

register_lock = threading.Lock()
def register_with_retry():

    from app.server.register import register, get_local_ip

    update_tray("Connecting")

    attempts = 1
    while attempts < 10:
        success = register(SERVER_URL, port=8765)
        if success:
            local_ip = get_local_ip()
            start_heartbeat_thread(SERVER_URL, local_ip)
            start_websocket_thread(local_ip)
            update_tray("Connected")
            logger.info("Host registered, heartbeat and WebSocket server started.")
            return
        else:
            retry_after = attempts ** 2 + 5
            notify(f"Registration failed. Retrying in {retry_after} seconds.")
            logger.info(f"Registration failed. Retrying in {retry_after} seconds.")
            time.sleep(retry_after)
            attempts += 1

    update_tray("Disconnected")
    notify("Registration failed. Please reconnect manually from the menu.")
    logger.error("Registration failed.")


### tray icon ###############################

from app.host.systemtray import setup_tray, update_tray
import app.host.systemtray as systemtray  # Assign register_with_retry

# Add after defining register_with_retry
systemtray.register_with_retry = register_with_retry

### main function ###############################

SERVER_URL = "http://skyboxx.tplinkdns.com:8000"

def main():
    logger.info("Application started.")

    # Get server URL
    if len(sys.argv) > 1:
        global SERVER_URL
        SERVER_URL = sys.argv[1]
        logger.info(f"Server URL set from command-line argument: {SERVER_URL}")
    else:
        logger.info(f"Using default server URL: {SERVER_URL}")

    # Hidden Tk window (needed only once)
    root = tk.Tk()
    root.withdraw()
    systemtray.root = root

    # Start connection thread
    register_thread = threading.Thread(target=register_with_retry, daemon=True)
    register_thread.start()

    threading.Thread(target=setup_tray, daemon=True).start()
    root.mainloop()
    logger.info("Application exited.")
    
if __name__ == "__main__":
    main()
