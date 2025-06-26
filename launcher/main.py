import sys

from launcher.modules.version_utils import get_installed_version, get_latest_version
from launcher.modules.installer import install_release, cleanup
from launcher.modules.config import is_auto_update_enabled, is_force_update_mode
from launcher.modules.launcher import prevent_mistaken_launch, launch_app
from launcher.modules.window import UpdaterWindow

def main():
    # 1. 重複起動
    if not prevent_mistaken_launch():
        sys.exit()
    
    # 2. ウィンドウの初期化
    window = UpdaterWindow()
    window.run_in_thread()
    window.set_status("Preparing to launch...")
    
    # 3. アプデ
    installed_version = get_installed_version()
    if installed_version is None or is_auto_update_enabled() or is_force_update_mode():
        window.set_status("Checking for updates...")
        latest_version = get_latest_version()
        if installed_version != latest_version:
            install_release(latest_version, window)
    # 4. 起動
    window.set_status("Launching application...")
    cleanup()
    launch_app()
    
    window.close()

if __name__ == "__main__":
    main()
