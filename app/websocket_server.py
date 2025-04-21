
import asyncio
import websockets
import json

connected_clients = set()

async def handler(websocket: websockets.WebSocketServerProtocol):
    print("📲 クライアント接続:", websocket.remote_address)
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print("📩 受信:", message)
            entry = {
                "type": "message",
                "message": "📤 受け取ったよ: " + message}
            await websocket.send(json.dumps(entry))
    except websockets.ConnectionClosed:
        print("🔌 切断されました:", websocket.remote_address)
    finally:
        print("🔌 切断されました:", websocket.remote_address)
        connected_clients.remove(websocket)

async def run_websocket_server(local_ip: str, port: int = 8765):
    server = await websockets.serve(handler, host="0.0.0.0", port=port)
    print(f"✅ WebSocketサーバー起動中 : ws://{local_ip}:{port}")
    await server.wait_closed()
