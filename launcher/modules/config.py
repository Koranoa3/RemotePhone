import json
import sys

CONFIG_PATH = "host_config.json"

def is_force_update_mode() -> bool:
    return "--force-update" in sys.argv

def is_auto_update_enabled() -> bool:
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("application", {}).get("enable_auto_update", False)
    except FileNotFoundError:
        print("[Warning] Configuration file not found. Auto-update is disabled.")
        return False
    except json.JSONDecodeError:
        print("[Error] Invalid configuration file format. Auto-update is disabled.")
        return False
    except Exception as e:
        print(f"[Error] Unexpected error reading config: {e}")
        return False