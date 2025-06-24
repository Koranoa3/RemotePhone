import asyncio, time, websockets, json
from app.client.authenticator import on_auth_start, handle_auth_response
from app.client.interactables import trackpad, action, volume, button

from logging import getLogger
logger = getLogger(__name__)

from app.host.notifer import notify, NotificationCategory
from app.config_io import set_client_attribute
from app.client.clients_manager import update_last_connection

HEARTBEAT_INTERVAL = 3  # seconds
HEARTBEAT_TIMEOUT = 6  # disconnect if pong is not received within this time

async def handle_client(websocket):
    last_pong = time.time()

    async def heartbeat():
        nonlocal last_pong
        while True:
            if not websocket.authenticated:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                continue
            timestamp = int(time.time() * 1000)  # convert to milliseconds
            ping_msg = json.dumps({"type": "ping", "timestamp": timestamp})
            try:
                await websocket.send(ping_msg)
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                if time.time() - last_pong > HEARTBEAT_TIMEOUT:
                    logger.warning("Disconnecting due to missing pong")
                    await websocket.close(code=1001, reason="pong timeout")
                    break
            except websockets.ConnectionClosedOK as e:
                break
            except: # TODO: ちゃんとエラー内容をログに出力する
                logger.error("Failed to send ping")
                break

    async def listen():
        nonlocal last_pong
        try:
            async for message in websocket:

                try:
                    data = json.loads(message)
                except Exception:
                    logger.error(f"Failed to decode JSON: {message}")
                    continue

                try:
                    msg_type = data.get("type", None)
                    msg_sender = data.get("sender", None)
                    if not websocket.authenticated:
                        if msg_type == "auth_start":
                            await on_auth_start(websocket, data["uuid"])

                        elif msg_type == "auth_response":
                            await handle_auth_response(websocket, data["onetime"])

                    elif msg_type == "pong":
                        now = int(time.time() * 1000)
                        rtt = now - data["timestamp"]
                        last_pong = time.time()
                        update_last_connection(websocket.uuid) # TODO: 接続状態の更新方法を改善
                        await websocket.send(json.dumps({"type": "rtt", "rtt": rtt}))

                    elif msg_type.startswith("tp_"):
                        trackpad.handle_event(data["type"], data)

                    elif msg_type.startswith("volume_"):
                        response = volume.handle_event(data["type"], data)
                        await respond(websocket, msg_sender, response)

                    elif msg_type == "action":
                        response = action.handle_action(data)
                        await respond(websocket, msg_sender, response)

                    elif msg_type == "vk":
                        response = action.handle_vk(data)
                        await respond(websocket, msg_sender, response)

                    elif msg_type == "button":
                        response = button.handle_mousebutton(data)
                        await respond(websocket, msg_sender, response)

                    elif msg_type == "get_config":
                        with open("client_config.json", "r", encoding="utf-8") as f:
                            config_data = json.load(f)
                        await websocket.send(json.dumps({"type": "config", "config": config_data}))

                    elif msg_type == "prefered_layout_mode":
                        layout_mode = data.get("layout_mode")
                        set_client_attribute("prefered_layout_mode", layout_mode)
                    else:
                        logger.info(f"Message with unrecognized type: {data}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except websockets.ConnectionClosedOK as e:
            if e.code == 1001:
                logger.info("Disconnected: Client left")
            elif e.code == 4003:
                logger.info("Disconnected: Authentication failed")
            else:
                logger.warning(f"Disconnected: Abnormal termination: {e.code} - {e.reason}")
        except websockets.ConnectionClosedError as e:
            if e.code == 1006:
                logger.warning("Disconnected: Connection state disappeared")
        finally:
            notify(NotificationCategory.ON_DISCONNECT, "Client has disconnected.")
            if websocket.authenticated and websocket.uuid:
                update_last_connection(websocket.uuid)

    await asyncio.gather(heartbeat(), listen())

async def respond(ws, sender, response):
    if response and sender:
        await ws.send(json.dumps({"type": "response", "target": sender, "response": response}))