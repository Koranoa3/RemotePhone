import websockets
from app.client.eventhandler import handle_client

from logging import getLogger
import asyncio, threading
logger = getLogger(__name__)

connected_clients = set()

async def handler(websocket):
    logger.info(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)

    websocket.authenticated = False
    await handle_client(websocket)

    connected_clients.remove(websocket)
    logger.info(f"WebSocket discarded: {websocket.remote_address}")


websocket_server = None
stop_event = threading.Event()

async def run_websocket_server(local_ip: str, port: int = 8765):
    global websocket_server
    if websocket_server:
        while websocket_server is not None:
            await asyncio.sleep(1)
        
    stop_event.clear()
    
    websocket_server = await websockets.serve(handler, host="0.0.0.0", port=port)
    logger.info(f"WebSocket server running: ws://{local_ip}:{port}")
    while not stop_event.is_set():
        await asyncio.sleep(0.1)
    await websocket_server.wait_closed()
    websocket_server = None

def stop_websocket_server():
    stop_event.set()
    if websocket_server:
        websocket_server.close()