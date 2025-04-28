import websockets
from app.client.eventhandler import handle_client

from app.notifer import notify

from logging import getLogger
import asyncio
logger = getLogger(__name__)

connected_clients = set()

async def handler(websocket):
    logger.info(f"クライアント接続: {websocket.remote_address}")
    connected_clients.add(websocket)

    websocket.authenticated = False
    await handle_client(websocket)

    connected_clients.remove(websocket)
    logger.info(f"websocketが廃棄されました: {websocket.remote_address}")


websocket_server = None
async def run_websocket_server(local_ip: str, port: int = 8765):
    global websocket_server
    if websocket_server:
        logger.info("WebSocketサーバーは既に起動しています。")
        return
    
    websocket_server = await websockets.serve(handler, host="0.0.0.0", port=port)
    logger.info(f"WebSocketサーバー起動中 : ws://{local_ip}:{port}")
    try:
        async with websocket_server:
            await websocket_server.wait_closed()
    except:
        logger.info("WebSocketサーバーを停止します。")
        if websocket_server:
            websocket_server.close()
            await websocket_server.wait_closed()
            websocket_server = None
    finally:
        logger.info("WebSocketサーバーが停止しました。")
