import requests

from logging import getLogger
logger = getLogger(__name__)

def check_for_updates(address: str, current_version: str) -> None:
    """
    Check for updates to the application.
    """
    logger.info("アップデートを確認中...")
    try:
        res = requests.get(address)
        res.raise_for_status()
        update_info = res.json()
        if update_info.get("version") != current_version:
            logger.info("アップデートが利用可能です。")
            logger.info(f"新しいバージョン: {update_info.get('version')}")
            logger.info(f"リリースURL: {update_info.get('download_url', '不明')}")
        else:
            logger.info("最新のバージョンです。")
    except requests.exceptions.RequestException as e:
        logger.error(f"アップデート確認失敗: {type(e.__cause__)}")
    except Exception as e:
        logger.error("アップデート確認失敗:", e)

    