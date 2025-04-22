import asyncio, time, websockets, json
from client.authenticator import on_auth_start, handle_auth_response
from client.interactables import trackpad, action, volume

HEARTBEAT_INTERVAL = 3  # 秒
HEARTBEAT_TIMEOUT = 6  # 秒以内にpongが返らなければ切断

async def handle_client(websocket):
    last_pong = time.time()

    async def heartbeat():
        nonlocal last_pong
        try:
            while True:
                if not websocket.authenticated:
                    await asyncio.sleep(HEARTBEAT_INTERVAL)
                    continue
                timestamp = int(time.time() * 1000) # ミリ秒に変換
                ping_msg = json.dumps({"type": "ping", "timestamp": timestamp})
                await websocket.send(ping_msg)
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                if time.time() - last_pong > HEARTBEAT_TIMEOUT:
                    print("💔 pongが返ってこないので切断")
                    await websocket.close()
                    break
        except websockets.ConnectionClosed as e:
            if e.code == 1001:
                print("👋 切断: クライアントが離脱")
            elif e.code == 4003:
                print("🔑 切断: 認証失敗")
            else:
                print(f"⚠️ 切断: 異常終了: {e.code} - {e.reason}")
        except Exception as e:
            print("🛑 Heartbeatエラー:", e)

    async def listen():
        nonlocal last_pong
        async for message in websocket:

            try:
                data = json.loads(message)
            except Exception:
                continue

            if not websocket.authenticated:
                if data.get("type") == "auth_start":
                    await on_auth_start(websocket, data["uuid"])

                elif data.get("type") == "auth_response":
                    success = await handle_auth_response(websocket, data["onetime"])
            
            elif data.get("type") == "pong":
                now = int(time.time() * 1000)
                rtt = now - data["timestamp"]
                last_pong = time.time()
                await websocket.send(json.dumps({"type": "rtt", "rtt": rtt}))
                # print(f"📶 pong受信 RTT: {rtt}ms")
            
            elif data.get("type").startswith("tp_"):
                trackpad.handle_event(data["type"], data)

            elif data.get("type").startswith("volume_"):
                volume.handle_event(data["type"], data)
                
            elif data.get("type") == "action":
                action.handle_event(data)
                
            else:
                print("📩 通常メッセージ:", data)

    await asyncio.gather(heartbeat(), listen())
