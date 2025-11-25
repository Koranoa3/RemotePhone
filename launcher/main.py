import sys
import threading
from tkinter import messagebox

from launcher.modules.version_utils import get_installed_version, get_latest_version
from launcher.modules.installer import install_release, cleanup
from launcher.modules.config import is_auto_update_enabled, is_force_update_mode
from launcher.modules.launcher import prevent_mistaken_launch, launch_app
from launcher.modules.window import UpdaterWindow
from launcher.modules.logger import setup_logger, get_logger

# Initialize logger at the start
setup_logger()
logger = get_logger(__name__)

def run(window):
    logger.info("Launcher started")
    window.set_status("Preparing to launch...")
    
    # 2. アプデ
    installed_version = get_installed_version()
    if installed_version is None or is_auto_update_enabled() or is_force_update_mode():
        window.set_status("Checking for updates...")
        latest_version = get_latest_version()
        force_update = installed_version is None or latest_version is None or is_force_update_mode()
        if installed_version != latest_version or force_update:
            logger.info(f"Update available: {installed_version} -> {latest_version}")
            if install_release(latest_version, window, force_update):
                window.set_status("Update completed successfully.")
                logger.info("Update completed successfully")
            else:
                logger.error("Failed to update the application")
                messagebox.showerror("Error", "Failed to update the application. Please try again later.")
                window.close()
                return
        else:
            logger.info(f"Already up to date: {installed_version}")
    else:
        logger.info(f"Auto-update disabled. Using installed version: {installed_version}")

    # 3. 起動
    window.set_status("Launching application...")
    logger.info("Cleaning up old versions")
    cleanup()
    logger.info("Launching application")
    launch_app()
    
    window.close()
    logger.info("Launcher finished")

def main():
    # 1. 重複起動
    if not prevent_mistaken_launch():
        sys.exit()

    window = UpdaterWindow()
    threading.Thread(target=run, args=(window,), daemon=True).start()
    window.run()
    

if __name__ == "__main__":
    main()
