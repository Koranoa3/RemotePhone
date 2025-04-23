import asyncio, time, websockets, json
from app.client.authenticator import on_auth_start, handle_auth_response
from app.client.interactables import trackpad, action, volume

from logging import getLogger
logger = getLogger(__name__)

from app.notifer import notify

HEARTBEAT_INTERVAL = 3  # 秒
HEARTBEAT_TIMEOUT = 6  # 秒以内にpongが返らなければ切断

async def handle_client(websocket):
    last_pong = time.time()

    async def heartbeat():
        nonlocal last_pong
        while True:
            if not websocket.authenticated:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                continue
            timestamp = int(time.time() * 1000) # ミリ秒に変換
            ping_msg = json.dumps({"type": "ping", "timestamp": timestamp})
            try:
                await websocket.send(ping_msg)
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                if time.time() - last_pong > HEARTBEAT_TIMEOUT:
                    logger.warning("pongが返ってこないので切断")
                    await websocket.close(code=1001, reason="pong timeout")
                    break
            except websockets.ConnectionClosedOK as e:
                break
            except:
                logger.error("ping送信失敗")
                break

    async def listen():
        nonlocal last_pong
        try:
            async for message in websocket:

                try:
                    data = json.loads(message)
                except Exception:
                    logger.error(f"JSONデコード失敗: {message}")
                    continue

                try:
                    msg_type = data.get("type", None)
                    if not websocket.authenticated:
                        if msg_type == "auth_start":
                            await on_auth_start(websocket, data["uuid"])

                        elif msg_type == "auth_response":
                            await handle_auth_response(websocket, data["onetime"])
                    
                    elif msg_type == "pong":
                        now = int(time.time() * 1000)
                        rtt = now - data["timestamp"]
                        last_pong = time.time()
                        await websocket.send(json.dumps({"type": "rtt", "rtt": rtt}))
                    
                    elif msg_type.startswith("tp_"):
                        trackpad.handle_event(data["type"], data)

                    elif msg_type.startswith("volume_"):
                        volume.handle_event(data["type"], data)
                        
                    elif msg_type == "action":
                        action.handle_action(data)
                    
                    elif msg_type == "vk":
                        action.handle_vk(data)

                    elif msg_type == "get_config":
                        with open("client_config.json", "r") as f:
                            config_data = json.load(f)
                        await websocket.send(json.dumps({"type": "config", "config": config_data}))

                    else:
                        logger.info(f"タイプ検知外のメッセージ:{data}")
                except Exception as e:
                    logger.error(f"メッセージ処理エラー: {e}")

        except websockets.ConnectionClosedOK as e:
            if e.code == 1001:
                logger.info("切断: クライアントが離脱")
            elif e.code == 4003:
                logger.info("切断: 認証失敗")
            else:
                logger.warning(f"切断: 異常終了: {e.code} - {e.reason}")
        except websockets.ConnectionClosedError as e:
            if e.code == 1006:
                logger.warning("切断: 接続状態が消滅")

    await asyncio.gather(heartbeat(), listen())
