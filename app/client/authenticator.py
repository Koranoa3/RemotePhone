import hashlib,time, json
def onetime_passkey(uuid: str) -> str: # UUIDと現在時刻から数字6桁のワンタイムパスワードを生成
    
    current_time = int(time.time())
    hash_object = hashlib.sha256(f"{uuid}{current_time}".encode())
    hash_hex = hash_object.hexdigest()

    otp = int(hash_hex, 16) % 1000000
    return f"{otp:06d}"  # 6桁のゼロパディングを保証


async def auth_start(websocket, uuid: str) -> dict:
    print("🔑 認証開始: ", uuid)
    auth_onetime = onetime_passkey(uuid)
    print("🔑 認証トークン:", auth_onetime)
    websocket.client_uuid = uuid
    websocket.auth_onetime = auth_onetime
    await websocket.send(json.dumps({"type": "auth_needed"}))

async def auth_response(websocket, uuid: str, onetime: str) -> dict:
    print("🔑 認証応答: ", onetime)
    if onetime == websocket.auth_onetime and uuid == websocket.client_uuid:
        await websocket.send(json.dumps({"type": "auth_result", "status": "ok"}))
        return True
    else:
        await websocket.send(json.dumps({"type": "auth_result", "status": "fail"}))
        return False