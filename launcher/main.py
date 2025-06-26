import sys
import threading

from launcher.modules.version_utils import get_installed_version, get_latest_version
from launcher.modules.installer import install_release, cleanup
from launcher.modules.config import is_auto_update_enabled, is_force_update_mode
from launcher.modules.launcher import prevent_mistaken_launch, launch_app
from launcher.modules.window import UpdaterWindow

def run(window):
    window.set_status("Preparing to launch...")
    
    # 2. アプデ
    installed_version = get_installed_version()
    if installed_version is None or is_auto_update_enabled() or is_force_update_mode():
        window.set_status("Checking for updates...")
        latest_version = get_latest_version()
        force_update = installed_version is None or latest_version is None or is_force_update_mode()
        if installed_version != latest_version or force_update:
            install_release(latest_version, window, force_update)
    # 3. 起動
    window.set_status("Launching application...")
    cleanup()
    launch_app()
    
    window.close()

def main():
    # 1. 重複起動
    if not prevent_mistaken_launch():
        sys.exit()

    window = UpdaterWindow()
    threading.Thread(target=run, args=(window,), daemon=True).start()
    window.run()
    

if __name__ == "__main__":
    main()
