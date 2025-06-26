import os
import sys
import shutil
import psutil
import requests
import platform
import tkinter.messagebox as messagebox
from updater.config import TEMP_DIR, APP_DIR_PREFIX, EXE_NAME
from updater.ui import UpdaterWindow
from updater.version import get_installed_version, get_latest_version, is_auto_update_enabled
from updater.downloader import download_update, extract_zip
from updater.cleaner import delete_old_app
from updater.launcher import launch_new_app
from updater.lock import create_lock

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
    
def main():
    if not is_windows():
        messagebox.showerror("Error", "This application is for Windows only.")
        sys.exit(1)

    if is_process_running(EXE_NAME):
        messagebox.showerror("Error", f"{EXE_NAME} is already running.")
        sys.exit(1)

    create_lock()

    window = UpdaterWindow()
    window.run_in_thread()
    window.set_status("Preparing to launch...")

    current_version, current_version_dir = get_installed_version()
    print(f"Current version: {current_version if current_version else 'None'}")

    app_dir = current_version_dir
    
    # ローカルにバージョンが何もなかったら / 自動アップデートが有効な場合は最新バージョンをダウンロード
    def download_latest_version():
        print("checking for updates...")
        window.set_status("Checking for updates...")
        
        latest_version = get_latest_version()
        if not latest_version:
            print("[Abort] Failed to fetch the latest version")
            messagebox.showerror("Error", "Failed to fetch version information.")
            return

        if current_version != latest_version:
            print("Starting download process.")
            window.set_status("Downloading latest version...")
            os.makedirs(TEMP_DIR, exist_ok=True)
            zip_path = os.path.join(TEMP_DIR, "update.zip")
            if download_update(zip_path, window):
                app_dir = f"{APP_DIR_PREFIX}{latest_version}"
                if os.path.exists(app_dir):
                    shutil.rmtree(app_dir)

                window.set_status("Extracting...")
                extract_zip(zip_path, app_dir)
                shutil.rmtree(TEMP_DIR)
                print("Download complete.")
            else:
                print("[Abort] Failed to download the update")
                window.set_status("Download failed.")

        
    if is_auto_update_enabled() or not current_version:
        download_latest_version()

    if app_dir and os.path.exists(app_dir):
        delete_old_app(window)
        print(f"Launching application from {app_dir}...")
        window.set_status("Launching...")
        new_app_path = os.path.join(app_dir, EXE_NAME)
        if os.path.exists(new_app_path):
            launch_new_app(new_app_path)
        else:
            print(f"Executable not found: {new_app_path}")
            messagebox.showerror("Error", f"Executable not found: {EXE_NAME}")
    else:
        print("Application not found.")
        window.set_status("Application not found.")
        messagebox.showerror("Error", "Application not found.")

    window.close()

if __name__ == "__main__":
    main()
