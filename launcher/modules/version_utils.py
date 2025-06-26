import os
import re
import requests

VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest/version"
APP_DIR_PREFIX = "app-"

def get_installed_version() -> str|None:
    versions = get_local_versions()
    return versions[0][0] if versions else None

def get_latest_version() -> str|None:
    try:
        res = requests.get(VERSION_INFO_URL, timeout=5)
        res.raise_for_status()
        return res.json().get("version")
    except Exception as e:
        print(f"[Error] Failed to fetch the latest version: {e}")
        return None

def get_local_versions() -> list[tuple[str, str]]: # [ ("v0.0.0", "app-v0.0.0") ]
    dirs = [d for d in os.listdir(".") if os.path.isdir(d) and d.startswith(APP_DIR_PREFIX)]
    versions = []
    for d in dirs:
        version = _parse_version_name(d)
        if version:
            versions.append((version, d))
    return sorted(versions, key=lambda x: _version_to_tuple(x[0]), reverse=True)

def get_latest_app_dir() -> str|None: # "app-v0.0.0"
    versions = get_local_versions()
    if versions:
        return versions[0][1]

def _parse_version_name(name) -> str|None:
    match = re.match(rf"{re.escape(APP_DIR_PREFIX)}(v\d+\.\d+\.\d+)", name)
    return match.group(1) if match else None

def _version_to_tuple(v) -> tuple[int, int, int]:
    return tuple(map(int, re.match(r"v(\d+)\.(\d+)\.(\d+)", v).groups()))
