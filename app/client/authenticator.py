import hashlib, time, json, os
from dataclasses import dataclass

from logging import getLogger
logger = getLogger(__name__)

from app.host.notifer import notify

registered_uuids_path = "registered_uuids.txt"
# --- Registered UUID ---
def if_uuid_registered(uuid: str) -> bool:
    if not os.path.exists(registered_uuids_path):
        open(registered_uuids_path, "w").close()
    with open(registered_uuids_path, "r+") as f:
        registered_uuids = f.read().splitlines()
    return uuid in registered_uuids

def register_uuid(uuid: str) -> bool:
    if if_uuid_registered(uuid):
        return False
    with open(registered_uuids_path, "a+") as f:
        f.write(uuid + "\n")
    return True

# --- OTP Generation ---
def onetime_passkey(uuid: str, timestamp: int = None) -> str:
    if timestamp is None:
        timestamp = int(time.time())
    hash_object = hashlib.sha256(f"{uuid}{timestamp}".encode())
    otp = int(hash_object.hexdigest(), 16) % 10000
    return f"{otp:04d}"

# --- Session Structure ---
@dataclass
class AuthSession:
    def __init__(self, uuid: str):
        self.uuid = uuid
        self.passkey = onetime_passkey(uuid)
        self.timestamp = int(time.time())
        self.attempt = 1

    def is_expired(self):
        return (int(time.time()) - self.timestamp) > 60


# --- Authentication Process ---
async def on_auth_start(ws, uuid: str):
    logger.info(f"Authentication started: {uuid}")
    if if_uuid_registered(uuid):
        logger.info("Authentication successful: UUID is already registered.")
        notify("Client has connected.")
        ws.authenticated = True
        await ws.send(json.dumps({"type": "auth_result", "status": "ok"}))
        return
    
    ws.auth = AuthSession(uuid=uuid)
    logger.info(f"Authentication OTP: {ws.auth.passkey}")
    notify(f"Authentication request received from client.\nOne-time key: {ws.auth.passkey}", duration=10, title="Authentication Request")
    await ws.send(json.dumps({"type": "auth_needed", "message": "Please enter the one-time key issued by the host."}))

async def send_auth_needed(ws, message: str, regenerate: bool = True):
    if not hasattr(ws, "auth"):
        logger.info("No authentication session found.")
        return

    if regenerate:
        ws.auth.passkey = onetime_passkey(ws.auth.uuid)
        ws.auth.timestamp = int(time.time())
        logger.info(f"Authentication OTP reissued: {ws.auth.passkey}")
        notify(f"Authentication request received again from client.\nOne-time key: {ws.auth.passkey}", duration=10, title="Authentication Request")

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

    await send_auth_needed(ws, f"{reason}. Please try again.", regenerate=True)
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
    if onetime != session.passkey:
        if session.attempt > 9:
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
