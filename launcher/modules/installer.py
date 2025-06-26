import os
import shutil
import time
import requests

MAX_RETRIES = 10
RELEASES_URL = "http://skyboxx.tplinkdns.com:8000/api/releases"
TEMP_DIR = "temp"
RETRY_DELAYS = [3, 5, 10, 20, 30]  # seconds

from launcher.modules.version_utils import get_local_versions, APP_DIR_PREFIX
from launcher.modules.window import UpdaterWindow

def install_release(version, window:UpdaterWindow) -> None:
    window.set_status("Downloading latest version...")
    os.makedirs(TEMP_DIR, exist_ok=True)
    zip_path = os.path.join(TEMP_DIR, "update.zip")
    for result in _download_update(version, zip_path):
        if result is True:
            app_dir = f"{APP_DIR_PREFIX}{version}"
            if os.path.exists(app_dir):
                shutil.rmtree(app_dir)
            print("Download complete.")
            window.set_status("Extracting update...")
            _extract_zip(zip_path, app_dir)
            print("Update extracted successfully.")
            break
        else:
            window.set_status(f"Download failed. Retrying in {result} seconds...")
            time.sleep(result)
    else:
        print("[Abort] Failed to download the update")

def cleanup() -> None:
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    versions = get_local_versions()
    for _, dir_name in versions[1:]:  # 最新を除く
        try:
            shutil.rmtree(dir_name)
        except Exception as e:
            print(f"[Error] Failed to delete old version: {e}")

def _download_update(version, zip_path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            download_url = f"{RELEASES_URL}/{version}/download"
            res = requests.get(download_url, timeout=10)
            res.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(res.content)
            yield True
            return True
        except Exception as e:
            print(f"[Retry {attempt}] Download failed: {e}")
            wait_time = RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)]
            for remaining in range(wait_time, 0, -1):
                yield remaining
                time.sleep(1)
    return False

def _extract_zip(zip_path, extract_to) -> None:
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

