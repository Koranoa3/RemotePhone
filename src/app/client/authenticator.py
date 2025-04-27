import hashlib, time, json, os
from dataclasses import dataclass

from logging import getLogger
logger = getLogger(__name__)

from app.notifer import notify

registered_uuids_path = "registered_uuids.txt"
# --- 認証済みUUID ---
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

# --- OTP生成 ---
def onetime_passkey(uuid: str, timestamp: int = None) -> str:
    if timestamp is None:
        timestamp = int(time.time())
    hash_object = hashlib.sha256(f"{uuid}{timestamp}".encode())
    otp = int(hash_object.hexdigest(), 16) % 10000
    return f"{otp:04d}"

# --- セッション構造体 ---
@dataclass
class AuthSession:
    def __init__(self, uuid: str):
        self.uuid = uuid
        self.passkey = onetime_passkey(uuid)
        self.timestamp = int(time.time())
        self.attempt = 1

    def is_expired(self):
        return (int(time.time()) - self.timestamp) > 60


# --- 認証処理 ---
async def on_auth_start(ws, uuid: str):
    logger.info(f"認証開始:{uuid}")
    if if_uuid_registered(uuid):
        logger.info("認証成功: UUIDは登録済みです。")
        notify("クライアントが接続されました。")
        ws.authenticated = True
        await ws.send(json.dumps({"type": "auth_result", "status": "ok"}))
        return
    
    ws.auth = AuthSession(uuid=uuid)
    logger.info(f"認証OTP:{ws.auth.passkey}")
    notify(f"クライアントから認証要求がありました。\nワンタイムキー:{ws.auth.passkey}", duration=15)
    await ws.send(json.dumps({"type": "auth_needed", "message": "ホストから発行されたワンタイムキーを入力してください。"}))

async def send_auth_needed(ws, message: str, regenerate: bool = True):
    if not hasattr(ws, "auth"):
        logger.info("認証セッションがありません。")
        return

    if regenerate:
        ws.auth.passkey = onetime_passkey(ws.auth.uuid)
        ws.auth.timestamp = int(time.time())
        logger.info(f"認証OTP再発行:{ws.auth.passkey}")
        notify(f"クライアントから再度認証要求がありました。\nワンタイムキー:{ws.auth.passkey}", duration=15)

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
        logger.info("認証成功")
        notify("クライアントが接続されました。")
        if register_uuid(ws.auth.uuid):
            logger.info("UUIDを登録しました。")
        else:
            logger.error("UUIDの登録に失敗しました。")
        return True

    logger.info(f"認証失敗: uuid:{ws.auth.uuid}, reason:{reason}")
    if not result.get("allow_retry", False):
        await ws.close(code=4003)
        return False

    
    await send_auth_needed(ws, f"{reason}。再度入力してください。", regenerate=True)
    return False

def check_response(ws, onetime: str) -> dict:
    session: AuthSession = getattr(ws, "auth", None)
    
    if not session:
        return {
            "type": "auth_result",
            "status": "fail",
            "reason": "セッションがありません",
            "allow_retry": False
        }
    if session.is_expired():
        return {
            "type": "auth_result",
            "status": "fail",
            "reason": "パスキーの有効期限が切れています",
            "allow_retry": True
        }
    if onetime != session.passkey:
        if session.attempt > 9:
            return {
                "type": "auth_result",
                "status": "fail",
                "reason": "試行回数が上限に達しました",
                "allow_retry": False
            }
        else:
            session.attempt += 1
            return {
                "type": "auth_result",
                "status": "fail",
                "reason": "パスキーが違います",
                "allow_retry": True
            }
    return {
        "type": "auth_result",
        "status": "ok"
    }