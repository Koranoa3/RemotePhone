


import os
import sys
import shutil
from pathlib import Path
import win32com.client  # `pywin32` パッケージが必要

from app.common import app_path

from logging import getLogger
logger = getLogger(__name__)

EXE_NAME = "RemotePhoneLauncher.exe"

def update_run_on_startup(enabled: bool):
    logger.info(f"Updating run on startup setting to: {enabled}")
    if enabled:
        add_to_startup("RemotePhone", f"{app_path(EXE_NAME)}")
    else:
        remove_from_startup("RemotePhone")

def add_to_startup(app_name: str, exe_path: str):
    logger.info(f"Adding {app_name} to startup with path: {exe_path}")
    if not exe_path or not Path(exe_path).exists():
        logger.error(f"Executable path does not exist: {exe_path}")
        return
    startup_dir = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_dir / f"{app_name}.lnk"

    shell = win32com.client.Dispatch("WScript.Shell")
    os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = exe_path
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    shortcut.IconLocation = exe_path
    shortcut.save()

def remove_from_startup(app_name: str):
    logger.info(f"Removing {app_name} from startup")
    startup_dir = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_dir / f"{app_name}.lnk"
    if shortcut_path.exists():
        shortcut_path.unlink()
