import shutil
from updater.version import get_local_versions

def delete_old_app(window):
    versions = get_local_versions()
    for _, dir_name in versions[1:]:  # 最新を除く
        try:
            window.set_status(f"Deleting {dir_name}...")
            shutil.rmtree(dir_name)
        except Exception as e:
            print(f"[Error] Failed to delete old version: {e}")
