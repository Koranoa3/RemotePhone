import os, json
from app.common import resource_path

from logging import getLogger
from typing import Any, Optional
logger = getLogger(__name__)


# Client Config Management
CLIENT_CONFIG_PATH = resource_path("client_config.json")

def load_client_config() -> dict:
    if not os.path.exists(CLIENT_CONFIG_PATH):
        return {}
    with open(CLIENT_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_client_config(config: dict):
    with open(CLIENT_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        
def get_client_attribute(key: str) -> Optional[Any]:
    config = load_client_config()
    if key not in config:
        logger.warning(f"Requested non-set attribute '{key}' in client config")
        return None
    return config[key]

def set_client_attribute(key: str, value):
    config = load_client_config()
    config[key] = value
    save_client_config(config)

# Host Config Management
HOST_CONFIG_PATH = resource_path("host_config.json")

def load_host_config() -> dict:
    if not os.path.exists(HOST_CONFIG_PATH):
        return {}
    with open(HOST_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_host_config(config: dict):
    with open(HOST_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_host_attribute(key: str) -> Optional[Any]:
    config = load_host_config()
    if key not in config:
        logger.warning(f"Requested non-set attribute '{key}' in host config")
        return None
    return config[key]

def set_host_attribute(key: str, value):
    config = load_host_config()
    config[key] = value
    save_host_config(config)


if __name__ == "__main__":
    # Example usage
    client_config = load_client_config()
    print("Client Config:", client_config, end="\n------------------\n")
    
    host_config = load_host_config()
    print("Host Config:", host_config, end="\n------------------\n")

    host_attribute = get_host_attribute("example_key")
    print("Get Host Attribute:", host_attribute, end="\n------------------\n")

    set_host_attribute("example_key", "example_value")
    print("Updated Host Config:", load_host_config(), end="\n------------------\n")