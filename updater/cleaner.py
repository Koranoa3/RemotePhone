import os
import shutil
import re
from version import get_local_versions

def delete_old_app(window):
    versions = get_local_versions()
    for _, dir_name in versions[1:]:  # 最新を除く
        try:
            window.set_status(f"{dir_name} を削除中...")
            shutil.rmtree(dir_name)
        except Exception as e:
            print(f"[Error] 古いバージョン削除失敗: {e}")
