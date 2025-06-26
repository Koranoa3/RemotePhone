import platform
import psutil
import os
import subprocess
import tempfile
import atexit
import tkinter.messagebox as messagebox

from launcher.modules.version_utils import get_latest_app_dir

EXE_NAME = "RemotePhoneHost.exe"
LOCK_FILE = os.path.join(tempfile.gettempdir(), 'RemotePhoneLauncher.lock')

def prevent_mistaken_launch() -> bool:
    if not _is_windows():
        messagebox.showerror("Error", "This application is for Windows only.")
        return False

    if _is_process_running(EXE_NAME):
        messagebox.showerror("Error", f"{EXE_NAME} is already running.")
        return False
    
    return _create_lock()


def launch_app() -> None:
    app_path = f"{get_latest_app_dir()}/{EXE_NAME}"
    if not os.path.exists(app_path):
        messagebox.showerror("Error", f"Application not found: {app_path}")
        return
    try:
        subprocess.Popen([app_path], shell=False)
    except Exception as e:
        print(f"[Error] Failed to launch the new app: {e}") 


def _is_windows() -> bool:
    return platform.system() == "Windows"


def _is_process_running(name) -> bool:
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def _create_lock() -> bool:
    if os.path.exists(LOCK_FILE):
        print("The application is already running. Exiting.")
        return False
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    atexit.register(_remove_lock)
    return True


def _remove_lock() -> None:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

