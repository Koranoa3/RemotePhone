import os
import tempfile

VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest/version"
DOWNLOAD_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest/download"
TEMP_DIR = "temp"
APP_DIR_PREFIX = "app-"
EXE_NAME = "RemotePhoneHost.exe"
MAX_RETRIES = 10
LOCK_FILE = os.path.join(tempfile.gettempdir(), 'updater.lock')
