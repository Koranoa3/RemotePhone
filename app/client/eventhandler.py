import asyncio, time, websockets, json
from client.authenticator import auth_start, auth_response

HEARTBEAT_INTERVAL = 3  # 秒
HEARTBEAT_TIMEOUT = 6  # 秒以内にpongが返らなければ切断

async def handle_client(websocket):
    last_pong = time.time()

    async def heartbeat():
        nonlocal last_pong
        try:
            while True:
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
                print("👋 クライアントが離脱")
            elif e.code == 4003:
                print("🔑 認証失敗")
            else:
                print(f"⚠️ 異常終了: {e.code} - {e.reason}")
        except Exception as e:
            print("🛑 Heartbeatエラー:", e)

    async def listen():
        nonlocal last_pong
        async for message in websocket:
            try:
                data = json.loads(message)
            except Exception:
                continue

            if data.get("type") == "pong":
                # now = int(time.time() * 1000)
                # rtt = now - data["timestamp"]
                # print(f"📶 pong受信 RTT: {rtt}ms")
                last_pong = time.time()
            
            elif data.get("type") == "auth_start":
                await auth_start(websocket, data["uuid"])

            elif data.get("type") == "auth_response":
                status = await auth_response(websocket, data["uuid"], data["onetime"])
                if status:
                    print("✅ 認証成功")
                else:
                    print("❌ 認証失敗")
                    await websocket.close(code=4003)
                    break

            else:
                print("📩 通常メッセージ:", data)

    await asyncio.gather(heartbeat(), listen())
