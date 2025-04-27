import requests

from logging import getLogger
logger = getLogger(__name__)

# 自分のバージョン

def parse_version(v):
    return [int(x) for x in v.lstrip('v').split('.')]

def get_latest_release_tag(repo):
    url = f"https://api.github.com/repos/{repo}/releases"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    releases = response.json()
    for release in releases:
        if not release.get("prerelease", False):
            return release["tag_name"]
    return None

def is_update_available(current_version) -> bool:
    repo = "KoralMint/RemotePhone"
    latest_tag = get_latest_release_tag(repo)
    if latest_tag is None:
        logger.info("正式リリースが見つかりませんでした。")
        return

    if parse_version(latest_tag) > parse_version(current_version):
        logger.info(f"アップデート可能！ 最新版は {latest_tag}")
    else:
        logger.info("最新バージョンです。")

if __name__ == "__main__":
    is_update_available()
