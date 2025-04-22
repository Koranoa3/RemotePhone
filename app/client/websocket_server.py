import websockets
from client.eventhandler import handle_client

connected_clients = set()

async def handler(websocket):
    print("📲 クライアント接続:", websocket.remote_address)
    connected_clients.add(websocket)

    websocket.authenticated = False
    await handle_client(websocket)

    connected_clients.remove(websocket)
    print("🗑️ websocketが廃棄されました:", websocket.remote_address)


async def run_websocket_server(local_ip: str, port: int = 8765):
    server = await websockets.serve(handler, host="0.0.0.0", port=port)
    print(f"✅ WebSocketサーバー起動中 : ws://{local_ip}:{port}")
    await server.wait_closed()