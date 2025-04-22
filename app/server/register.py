import socket
import requests
from dataclasses import dataclass

@dataclass
class HostInfo:
    name: str
    local_ip: str
    port: int
    password: str

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def register(server_url: str, port: int = 8765, password: str="") -> bool:
    host_info = HostInfo(
        name=socket.gethostname(),
        local_ip=get_local_ip(),
        port=port,
        password=password
    )

    try:
        res = requests.post(f"{server_url}/api/register", json={
            "name": host_info.name,
            "local_ip": host_info.local_ip,
            "port": host_info.port
        })
        res.raise_for_status()
        print("登録結果:", res.json())
        return True
    except Exception as e:
        print("登録失敗:", e)
        return False
