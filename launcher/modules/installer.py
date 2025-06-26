import os
import shutil
import time
import requests
import zipfile

MAX_RETRIES = 10
MAX_TIMEOUT = 10
RELEASES_URL = "http://skyboxx.tplinkdns.com:8000/api/releases"
TEMP_DIR = "temp"
RETRY_DELAYS = [3, 5, 10, 20, 30]  # seconds

from launcher.modules.version_utils import get_local_versions, APP_DIR_PREFIX
from launcher.modules.window import UpdaterWindow

def install_release(version, window:UpdaterWindow, force_retry:False) -> bool:
    print(("[force update]" if force_retry else "")+"Downloading version:", version)
    window.set_status("Downloading latest version...")
    os.makedirs(TEMP_DIR, exist_ok=True)
    zip_path = os.path.join(TEMP_DIR, "update.zip")
    for result in _download_update(version, zip_path, force_retry):
        if result is True:
            app_dir = f"{APP_DIR_PREFIX}{version}"
            if os.path.exists(app_dir):
                shutil.rmtree(app_dir)
            print("Download complete.")
            
            window.set_status("Extracting update...")
            if _extract_zip(zip_path, app_dir):
                print("Update extracted successfully.")
                return True
            else:
                print("[Abort] Failed to extract the update")
                window.set_status("Failed to extract update.")
                cleanup()
                time.sleep(1)
                return False
        elif type(result) is int:
            if result == 0:
                window.set_status("Downloading latest version...")
            else:
                window.set_status(f"Download failed. Retrying in {result} seconds...")
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

def _download_update(version, zip_path, force_retry=False):
    attempt = 1
    while force_retry or attempt <= MAX_RETRIES:
        print(f"[Attempt {attempt}] Downloading version {version}...")
        try:
            download_url = f"{RELEASES_URL}/{version}/download"
            res = requests.get(download_url, timeout=MAX_TIMEOUT)
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
            yield 0
            attempt += 1
    return False

def _extract_zip(zip_path, extract_to) -> bool:
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except zipfile.BadZipFile as e:
        print(f"[Error] Bad zip file: {e}")
    except Exception as e:
        print(f"[Error] Failed to extract zip file: {e}")
    return False
