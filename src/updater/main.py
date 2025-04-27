import os
import re
import shutil
import zipfile
import requests
import subprocess
import time

# 設定
VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest/version"
DOWNLOAD_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest/download"
TEMP_DIR = "temp"
APP_DIR_PREFIX = "app-"
EXE_NAME = "RemotePhoneHost.exe"
MAX_RETRIES = 10

def get_current_version():
    app_dirs = [d for d in os.listdir(".") if os.path.isdir(d) and d.startswith(APP_DIR_PREFIX)]
    versions = []
    pattern = re.compile(r"app-(v\d+\.\d+\.\d+)")
    for d in app_dirs:
        match = pattern.match(d)
        if match:
            versions.append((match.group(1), d))
    if not versions:
        return None, None
    versions.sort(reverse=True)
    return versions[0][0], versions[0][1]

def get_latest_version():
    try:
        res = requests.get(VERSION_INFO_URL, timeout=5)
        res.raise_for_status()
        data = res.json()
        return data.get("version")
    except Exception as e:
        print(f"[Error] 最新バージョン取得失敗: {e}")
        return None

def download_update(zip_path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = requests.get(DOWNLOAD_URL, timeout=10)
            res.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            print(f"[Retry {attempt}] ダウンロード失敗: {e}")
            time.sleep(min(2 ** attempt, 60))  # 指数バックオフ、最大60秒待機
    return False

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def launch_new_app(app_path):
    try:
        subprocess.Popen([app_path], shell=False)
    except Exception as e:
        print(f"[Error] 新アプリ起動失敗: {e}")

def main():
    # tempディレクトリ初期化
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    current_version, current_dir = get_current_version()
    print(f"現行バージョン: {current_version if current_version else 'なし'}")

    latest_version = get_latest_version()
    if not latest_version:
        print("[Abort] 最新バージョン取得に失敗")
        return

    print(f"最新バージョン: {latest_version}")

    if current_version == latest_version:
        print("すでに最新バージョンです。起動します。")
        new_app_path = os.path.join(current_dir, EXE_NAME)
        launch_new_app(new_app_path)
        return

    # アップデート処理
    print("アップデートを開始します。")
    zip_path = os.path.join(TEMP_DIR, "update.zip")
    if not download_update(zip_path):
        print("[Abort] ダウンロード失敗。アップデートを中止します。")
        return

    new_dir = f"{APP_DIR_PREFIX}{latest_version}"
    if os.path.exists(new_dir):
        shutil.rmtree(new_dir)

    extract_zip(zip_path, new_dir)
    print("アップデート完了。新しいバージョンを起動します。")

    new_app_path = os.path.join(new_dir, EXE_NAME)
    launch_new_app(new_app_path)

if __name__ == "__main__":
    main()
