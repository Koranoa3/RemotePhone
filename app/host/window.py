import webview
import multiprocessing

from logging import getLogger
logger = getLogger(__name__)

Process = multiprocessing.Process
webview_process:Process = None

webview.gui = 'cef'

from app.host.window_api import Api

def run_webview():
    """
    Create a webview window.
    """
    api =  Api()
    webview.create_window(
        "RemotePhone", "resources/window.html",
        width=1024, height=769, background_color="#3a4750",
        resizable=True, min_size=(800, 480),
        js_api=api
    )
    webview.start(debug=False)

def start_webview_process():
    global webview_process
    if not webview_process or not webview_process.is_alive():
        logger.info("Starting webview process.")
        webview_process = Process(target=run_webview)
        webview_process.start()

def stop_webview_process():
    global webview_process
    if webview_process and webview_process.is_alive():
        logger.info("Stopping webview process.")
        webview_process.terminate()
        webview_process.join()
    webview_process = None
    logger.info("Webview process stopped.")