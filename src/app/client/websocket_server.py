import websockets
from src.app.client.eventhandler import handle_client

from src.app.notifer import notify

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


websocket_server_task = None
async def run_websocket_server(local_ip: str, port: int = 8765):
    global websocket_server_task

    if websocket_server_task and not websocket_server_task.done():
        logger.info("WebSocketサーバーは既に起動中です。")
        return

    async def server_task():
        logger.info("WebSocketサーバーを起動中...")
        server = await websockets.serve(handler, host="0.0.0.0", port=port)
        logger.info(f"WebSocketサーバー起動 : ws://{local_ip}:{port}")
        try:
            async with server:
                await server.wait_closed()
        except Exception as e:
            logger.error(f"WebSocketサーバーエラー: {e}")
        finally:
            logger.info("WebSocketサーバーが停止しました。")

    websocket_server_task = asyncio.create_task(server_task())
