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
        print(f"[Error] Failed to fetch the latest version: {e}")
        return None
    
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
    window.set_status("Checking for updates...")

    current_version, current_version_dir = get_current_version()
    print(f"Current version: {current_version if current_version else 'None'}")

    latest_version = get_latest_version()
    if not latest_version:
        print("[Abort] Failed to fetch the latest version")
        return

    print(f"Latest version: {latest_version}")

    app_dir = current_version_dir if current_version else None
    if not current_version == latest_version:
        print("Starting the update process.")
        window.set_status("Downloading update...")
        os.makedirs(TEMP_DIR, exist_ok=True)
        zip_path = os.path.join(TEMP_DIR, "update.zip")
        if download_update(zip_path, window):
            app_dir = f"{APP_DIR_PREFIX}{latest_version}"
            if os.path.exists(app_dir):
                shutil.rmtree(app_dir)

            window.set_status("Extracting...")
            extract_zip(zip_path, app_dir)
            shutil.rmtree(TEMP_DIR)
            print("Update complete. Launching the new version.")
        else:
            print("[Abort] Failed to download the update")

    if app_dir and os.path.exists(app_dir):
        delete_old_app(window)
        window.set_status("Launching...")
        new_app_path = os.path.join(app_dir, EXE_NAME)
        launch_new_app(new_app_path)
    else:
        print("Application not found.")
        window.set_status("Application not found.")

    window.close()

if __name__ == "__main__":
    main()
