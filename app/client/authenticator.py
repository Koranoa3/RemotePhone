import hashlib, time, json, os
from dataclasses import dataclass

from logging import getLogger
logger = getLogger(__name__)

from app.host.notifer import notify
from app.common import get_device_id

from app.client.clients_manager import if_uuid_registered, register_uuid, update_last_connection

# --- Current Passkey Management ---
KEY_EXPIRE = 30  # seconds
_current_key = None
_key_limit = None
_host_device_info: dict = {} # ハッシュ値を生成するためのデバイス情報

KEY_ATTEMPT_LIMIT = 9

def get_current_passkey() -> dict:
    global _current_key, _key_limit
    
    timestamp = int(time.time())
    # Check if key exists and is still valid
    if _current_key and _key_limit and timestamp < _key_limit:
        expire_in = KEY_EXPIRE - (timestamp % KEY_EXPIRE)
        return {"key": _current_key, "expire_in": expire_in}

    # Generate new key using onetime_passkey with uuid=None
    _current_key = onetime_passkey(timestamp=timestamp)
    _key_limit = timestamp + KEY_EXPIRE - (timestamp % KEY_EXPIRE)

    expire_in = KEY_EXPIRE - (timestamp % KEY_EXPIRE)
    return {"key": _current_key, "expire_in": expire_in}


# --- OTP Generation ---
def onetime_passkey(timestamp: int = None) -> str:
    global _host_device_info
    if not _host_device_info:
        # デバイス情報を初期化
        try:
            _host_device_info = {
                "device_name": os.uname().nodename if hasattr(os, "uname") else os.getenv("COMPUTERNAME", "unknown"),
                "user_name": os.getenv("USERNAME", "unknown"),
                "device_id": get_device_id()
            }
        except Exception:
            logger.warning("Failed to retrieve host device information, using default values.")
            _host_device_info = {
                "device_name": "unknown",
                "user_name": "unknown",
                "device_id": "unknown"
            }

    # デバイス名を取得
    device_name = _host_device_info.get("device_name", "unknown")
    user_name = _host_device_info.get("user_name", "unknown")
    device_id = _host_device_info.get("device_id", "unknown")

    if timestamp is None:
        timestamp = int(time.time())

    # KEY_EXPIREで区切った現在時刻
    time_block = int(timestamp // KEY_EXPIRE)
    hash_input = f"onetime{device_name}{user_name}{device_id}{time_block}"
    hash_object = hashlib.sha256(hash_input.encode())
    otp = int(hash_object.hexdigest(), 16) % 10000
    return f"{otp:04d}"

# --- Session Structure ---
@dataclass
class AuthSession:
    def __init__(self, uuid: str):
        self.uuid = uuid
        self.attempt = 1

    def is_expired(self):
        global _key_limit
        current_time = int(time.time())
        return not (_key_limit and current_time < _key_limit)


# --- Authentication Process ---
async def on_auth_start(ws, uuid: str):
    logger.info(f"Authentication started: {uuid}")
    ws.uuid = uuid
    if if_uuid_registered(uuid):
        logger.info("Authentication successful: UUID is already registered.")
        notify("Client has connected.")
        ws.authenticated = True
        update_last_connection(uuid)
        await ws.send(json.dumps({"type": "auth_result", "status": "ok"}))
        return
    
    ws.auth = AuthSession(uuid=uuid)
    passkey_info = get_current_passkey()
    passkey = passkey_info["key"]
    logger.info(f"Authentication OTP: {passkey}")
    notify(f"Authentication request received from client.\nOne-time key: {passkey}", duration=10, title="Authentication Request")
    await ws.send(json.dumps({"type": "auth_needed", "message": "Please enter the one-time key issued by the host."}))

async def send_auth_needed(ws, message: str):
    if not hasattr(ws, "auth"):
        logger.info("No authentication session found.")
        return

    passkey_info = get_current_passkey()
    passkey = passkey_info["key"]
    ws.auth.timestamp = int(time.time())
    logger.info(f"Authentication OTP reissued: {passkey}")
    notify(f"Authentication request received again from client.\nOne-time key: {passkey}", duration=10, title="Authentication Request")

    await ws.send(json.dumps({
        "type": "auth_needed",
        "message": message
    }))

async def handle_auth_response(ws, onetime: str):
    result = check_response(ws, onetime)
    await ws.send(json.dumps(result))

    status = result.get("status")
    reason = result.get("reason", "")

    if status == "ok":
        ws.authenticated = True
        logger.info("Authentication successful")
        notify("Client has connected.")
        if register_uuid(ws.auth.uuid):
            logger.info("UUID registered successfully.")
        else:
            logger.error("Failed to register UUID.")
        return True

    logger.info(f"Authentication failed: uuid: {ws.auth.uuid}, reason: {reason}")
    if not result.get("allow_retry", False):
        await ws.close(code=4003)
        return False

    await send_auth_needed(ws, f"{reason}. Please try again.")
    return False

def check_response(ws, onetime: str) -> dict:
    session: AuthSession = getattr(ws, "auth", None)
    
    if not session:
        return {
            "type": "auth_result",
            "status": "fail",
            "reason": "No session found",
            "allow_retry": False
        }
    if session.is_expired():
        return {
            "type": "auth_result",
            "status": "fail",
            "reason": "Passkey has expired",
            "allow_retry": True
        }
    
    passkey_info = get_current_passkey()
    current_passkey = passkey_info["key"]
    
    if onetime != current_passkey:
        if session.attempt > KEY_ATTEMPT_LIMIT:
            return {
                "type": "auth_result",
                "status": "fail",
                "reason": "Maximum number of attempts reached",
                "allow_retry": False
            }
        else:
            session.attempt += 1
            return {
                "type": "auth_result",
                "status": "fail",
                "reason": "Incorrect passkey",
                "allow_retry": True
            }
    return {
        "type": "auth_result",
        "status": "ok"
    }
