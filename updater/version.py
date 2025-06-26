import os
import re
import requests
import json
from updater.config import APP_DIR_PREFIX, VERSION_INFO_URL, CONFIG_PATH

def parse_version_name(name):
    match = re.match(r"app-(v\d+\.\d+\.\d+)", name)
    return match.group(1) if match else None

def version_to_tuple(v):
    return tuple(map(int, re.match(r"v(\d+)\.(\d+)\.(\d+)", v).groups()))

def get_local_versions():
    dirs = [d for d in os.listdir(".") if os.path.isdir(d) and d.startswith(APP_DIR_PREFIX)]
    versions = []
    for d in dirs:
        version = parse_version_name(d)
        if version:
            versions.append((version, d))
    return sorted(versions, key=lambda x: version_to_tuple(x[0]), reverse=True)

def get_installed_version():
    versions = get_local_versions()
    return versions[0] if versions else (None, None)

def get_latest_version():
    try:
        res = requests.get(VERSION_INFO_URL, timeout=5)
        res.raise_for_status()
        return res.json().get("version")
    except Exception as e:
        print(f"[Error] Failed to fetch the latest version: {e}")
        return None

def is_auto_update_enabled():
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