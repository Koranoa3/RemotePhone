
import asyncio
import websockets

connected_clients = set()

async def handler(websocket):
    print("📲 クライアント接続:", websocket.remote_address)
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print("📩 受信:", message)
            await websocket.send("📤 受け取ったよ: " + message)
    except websockets.ConnectionClosed:
        print("🔌 切断されました:", websocket.remote_address)
    finally:
        connected_clients.remove(websocket)

async def run_websocket_server(local_ip: str):
    server = await websockets.serve(handler, host="0.0.0.0", port=8765)
    print(f"✅ WebSocketサーバー起動中 : ws://{local_ip}:8765")
    await server.wait_closed()
