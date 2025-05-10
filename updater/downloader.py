import requests
import time
from config import MAX_RETRIES, DOWNLOAD_URL

def download_update(zip_path, window):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = requests.get(DOWNLOAD_URL, timeout=10)
            res.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            print(f"[Retry {attempt}] Download failed: {e}")
            wait_time = min(2 ** attempt, 60)
            for remaining in range(wait_time, 0, -1):
                window.set_status(f"Download failed. Retrying in {remaining} seconds...")
                time.sleep(1)
    return False

def extract_zip(zip_path, extract_to):
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

