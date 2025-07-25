import ctypes, json
from app.common import app_resource_path

from logging import getLogger
logger = getLogger(__name__)

# DLL input
ime = ctypes.CDLL(app_resource_path("ime_input.dll"))
ime.send_text.argtypes = [ctypes.c_wchar_p]
ime.send_text.restype = None


def send_string(text: str):
    ime.send_text(text)

def send_return():
    """Returnキーを送信する"""
    ime.return_key()

def handle_text_event(data):
    """キーボードイベントを処理する"""
    try:
        text = data.get("text", None)
        ent = data.get("ent", False)
        
        if not text and not ent:
            logger.warning("No text or ent provided in data")
            return
        elif not text and ent:
            send_return()
            return
        else:
            if isinstance(text, str) and (text.startswith("[") or text.startswith("{")):
                try:
                    text = json.loads(text)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON text: {e}")
            
            elif isinstance(text, str):
                send_string(text)
            
            elif isinstance(text, list):
                for line in text:
                    send_string(line)
            
            else:
                logger.error("Invalid text type: %s", type(text))
                return "Invalid"
            if ent:
                send_return()
    except Exception as e:
        logger.exception("Exception in handle_text_event: %s", e)
        return f"Error: {e}"