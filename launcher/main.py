import sys

from launcher.modules.version_utils import get_installed_version, get_latest_version, get_latest_app_dir
from launcher.modules.installer import install_latest_release, cleanup
from launcher.modules.config import is_auto_update_enabled, is_force_update_mode
from launcher.modules.launcher import prevent_mistaken_launch, launch_app

def main():
    # 1. 重複起動
    if not prevent_mistaken_launch():
        sys.exit()
    # 2. アプデ
    installed_version = get_installed_version()
    if installed_version is None or is_auto_update_enabled() or is_force_update_mode():
        if installed_version != get_latest_version():
            install_latest_release()
    # 3. 起動
    launch_app()

if __name__ == "__main__":
    main()
