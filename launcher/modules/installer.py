import os
import shutil
import time
import requests

MAX_RETRIES = 5
RELEASES_URL = "http://skyboxx.tplinkdns.com:8000/api/releases"
TEMP_DIR = "temp"

from launcher.modules.version_utils import get_local_versions, APP_DIR_PREFIX

def install_latest_release(version) -> None:
    os.makedirs(TEMP_DIR, exist_ok=True)
    zip_path = os.path.join(TEMP_DIR, "update.zip")
    if _download_update(version,zip_path):
        app_dir = f"{APP_DIR_PREFIX}{version}"
        if os.path.exists(app_dir):
            shutil.rmtree(app_dir)

        _extract_zip(zip_path, app_dir)
        shutil.rmtree(TEMP_DIR)
        print("Download complete.")
    else:
        print("[Abort] Failed to download the update")

def cleanup() -> None:
    versions = get_local_versions()
    for _, dir_name in versions[1:]:  # 最新を除く
        try:
            shutil.rmtree(dir_name)
        except Exception as e:
            print(f"[Error] Failed to delete old version: {e}")

def _download_update(version, zip_path) -> bool:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            download_url = f"{RELEASES_URL}/{version}/download"
            res = requests.get(download_url, timeout=10)
            res.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            print(f"[Retry {attempt}] Download failed: {e}")
            wait_time = min(2 ** attempt, 60)
            for remaining in range(wait_time, 0, -1):
                time.sleep(1)
    return False

def _extract_zip(zip_path, extract_to) -> None:
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

