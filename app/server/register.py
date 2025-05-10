import socket
import requests
from dataclasses import dataclass

from logging import getLogger
logger = getLogger(__name__)

@dataclass
class HostInfo:
    name: str
    local_ip: str
    port: int

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def register(server_url: str, port: int = 8765) -> bool:
    host_info = HostInfo(
        name=socket.gethostname(),
        local_ip=get_local_ip(),
        port=port
    )
    logger.info(f"Registering host information to the server: local_ip={host_info.local_ip}, port={host_info.port}")
    try:
        res = requests.post(f"{server_url}/api/register", json={
            "name": host_info.name,
            "local_ip": host_info.local_ip,
            "port": host_info.port
        })
        res.raise_for_status()
        logger.info(f"Host information registered: Global IP:{res.json().get('from_ip', 'Unknown')}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to register host information: {type(e.__cause__)}")
        return False
    except Exception as e:
        logger.error("Failed to register host information:", e)
        return False
