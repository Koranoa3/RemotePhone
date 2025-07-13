"""
Server using sockets to display a window when receiving the "show_window" command
"""

import socket
import threading

from logging import getLogger
logger = getLogger(__name__)

PORT = 63136

def handle_command(conn):
    data = conn.recv(1024).decode()
    if data == "show_window":
        logger.info("Received command to show window.")
        from app.host.window import start_webview_process
        start_webview_process()
    elif data == "exit":
        logger.info("Received command to exit.")
        from app.host.window import stop_webview_process
        stop_webview_process()
        import os
        os._exit(0)
    conn.close()

def command_server():
    """ run on thread! """
    logger.info("Starting command server on port %d", PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", PORT))
    server.listen()
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_command, args=(conn,), daemon=True).start()

