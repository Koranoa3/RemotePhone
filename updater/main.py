import os, sys
import re
import shutil
import zipfile
import requests
import subprocess
import time
import tkinter as tk
import threading
import atexit
import tempfile

# 設定
VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest/version"
DOWNLOAD_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest/download"
TEMP_DIR = "temp"
APP_DIR_PREFIX = "app-"
EXE_NAME = "RemotePhoneHost.exe"
MAX_RETRIES = 10
LOCK_FILE = os.path.join(tempfile.gettempdir(), 'updater.lock')

# --- アップデート処理 ---

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

def download_update(zip_path, window):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = requests.get(DOWNLOAD_URL, timeout=10)
            res.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            print(f"[Retry {attempt}] ダウンロード失敗: {e}")
            wait_time = min(2 ** attempt, 60)
            for remaining in range(wait_time, 0, -1):
                window.set_status(f"ダウンロード失敗。{remaining}秒後に再試行します...")
                time.sleep(1)
    return False

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def launch_new_app(app_path):
    try:
        subprocess.Popen([app_path], shell=False)
    except Exception as e:
        print(f"[Error] 新アプリ起動失敗: {e}")

def delete_old_app(window):
    app_dirs = [d for d in os.listdir(".") if os.path.isdir(d) and d.startswith(APP_DIR_PREFIX)]
    pattern = re.compile(r"app-(v\d+\.\d+\.\d+)")
    versions = []

    for d in app_dirs:
        match = pattern.match(d)
        if match:
            versions.append((match.group(1), d))

    if versions:
        versions.sort(
            key=lambda x: list(map(int, re.match(r"v(\d+)\.(\d+)\.(\d+)", x[0]).groups())),
            reverse=True
        )

    for _, dir_name in versions[1:]:  # Skip the latest version
        try:
            window.set_status(f"{dir_name} を削除中...")
            shutil.rmtree(dir_name)
        except Exception as e:
            print(f"[Error] 古いバージョン削除失敗: {e}")

# --- 多重起動防止防止 ---

def create_lock():
    if os.path.exists(LOCK_FILE):
        print("すでに起動しています。終了します。")
        sys.exit(1)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    atexit.register(remove_lock)

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# --- ステータスウィンドウ ---
class UpdaterWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RemotePhone Launcher")
        self.root.iconbitmap(default="app.ico")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)

        self.label = tk.Label(self.root, text="初期化中...", font=("Arial", 16))
        self.label.pack(expand=True)

    def set_status(self, text):
        self.label.config(text=text)
        self.root.update()

    def run_in_thread(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def close(self):
        self.root.destroy()

def main():
    # tempディレクトリ初期化
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    window = UpdaterWindow()
    window.run_in_thread()

    window.set_status("アップデートを確認中...")
    current_version, current_version_dir = get_current_version()
    print(f"現行バージョン: {current_version if current_version else 'なし'}")

    latest_version = get_latest_version()
    if not latest_version:
        print("[Abort] 最新バージョン取得に失敗")
        return

    print(f"最新バージョン: {latest_version}")

    app_dir = current_version_dir if current_version else None
    if not current_version == latest_version:
        # アップデート処理
        print("アップデートを開始します。")
        window.set_status("アップデートをダウンロード中...")
        zip_path = os.path.join(TEMP_DIR, "update.zip")
        if download_update(zip_path, window):
            app_dir = f"{APP_DIR_PREFIX}{latest_version}"
            if os.path.exists(app_dir):
                shutil.rmtree(app_dir)

            window.set_status("展開中...")
            extract_zip(zip_path, app_dir)
            shutil.rmtree(TEMP_DIR)
            print("アップデート完了。新しいバージョンを起動します。")
        else:
            print("[Abort] アップデートのダウンロードに失敗")
    else:
        print("最新バージョンです。")

    if app_dir and os.path.exists(app_dir):
        delete_old_app(window)
        
        window.set_status("起動中...")
        new_app_path = os.path.join(app_dir, EXE_NAME)
        launch_new_app(new_app_path)
    else:
        print("アプリケーションが見つかりません。")
        window.set_status("アプリケーションが見つかりません。")    
    
    window.close()

if __name__ == "__main__":
    create_lock()
    main()
