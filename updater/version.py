import os
import re
from config import APP_DIR_PREFIX

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

def get_current_version():
    versions = get_local_versions()
    return versions[0] if versions else (None, None)
