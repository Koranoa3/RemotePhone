import os
import sys
import shutil
import psutil
from config import TEMP_DIR, APP_DIR_PREFIX, EXE_NAME
from ui import UpdaterWindow
from version import get_current_version
from downloader import download_update, extract_zip
from cleaner import delete_old_app
from launcher import launch_new_app
from lock import create_lock
import requests
import platform
import tkinter.messagebox as messagebox

def is_windows():
    return platform.system() == "Windows"

def is_process_running(name):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def get_latest_version():
    from config import VERSION_INFO_URL
    try:
        res = requests.get(VERSION_INFO_URL, timeout=5)
        res.raise_for_status()
        return res.json().get("version")
    except Exception as e:
        print(f"[Error] 最新バージョン取得失敗: {e}")
        return None
    
def main():
    if not is_windows():
        messagebox.showerror("エラー", "このアプリケーションはWindows専用です。")
        sys.exit(1)

    if is_process_running(EXE_NAME):
        messagebox.showerror("エラー", f"すでに{EXE_NAME}が実行中です。")
        sys.exit(1)

    create_lock()

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
    main()
