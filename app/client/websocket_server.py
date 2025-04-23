import websockets
from client.eventhandler import handle_client

from notifer import notify

from logging import getLogger
logger = getLogger(__name__)

connected_clients = set()

async def handler(websocket):
    logger.info(f"クライアント接続: {websocket.remote_address}")
    connected_clients.add(websocket)

    websocket.authenticated = False
    await handle_client(websocket)

    connected_clients.remove(websocket)
    logger.info(f"websocketが廃棄されました: {websocket.remote_address}")


async def run_websocket_server(local_ip: str, port: int = 8765):
    server = await websockets.serve(handler, host="0.0.0.0", port=port)
    logger.info(f"WebSocketサーバー起動中 : ws://{local_ip}:{port}")
    try:
        async with server:
            await server.wait_closed()
    except:
        logger.info("WebSocketサーバーを停止します。")
        if server:
            server.close()
    finally:
        logger.info("WebSocketサーバーが停止しました。")
