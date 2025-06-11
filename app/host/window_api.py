
from logging import getLogger
logger = getLogger(__name__)


# --- APIクラス定義 ---
class HomeApi:
    def get_device_connection_status(self):
        # 仮実装
        return {
            "status": "connected",  # or "not connected"
            "device_name": "iPhone 15 Pro",
            "rtt": "安定",
            "since": "00:15:32"
        }

    def get_server_connection_status(self):
        # 仮実装
        return {
            "status": "ok"  # or "warn", "critical"
        }

    def get_communication_methods(self):
        # 仮実装
        return {
            "available": ["websocket", "webrtc"],
            "prefered": "websocket",
            "selected": "websocket"
        }

    def set_prefered_communication_method(self, method):
        logger.info(f"set_prefered_communication_method: {method}")
        # 仮実装
        return True

class ConnectApi:
    def get_current_passkey(self):
        # 仮実装
        return {
            "passkey": "1234",
            "remain": 25
        }

    def get_registered_devices(self):
        # 仮実装
        return [
            {"name": "iPhone 15 Pro", "uuid": "uuid-1", "last_connection": 0},
            {"name": "iPad Air", "uuid": "uuid-2", "last_connection": 4320}
        ]

    def delete_registered_device(self, uuid):
        logger.info(f"delete_registered_device: {uuid}")
        # 仮実装
        return True

class SettingsApi:
    _settings = {
        "system": {"run_on_startup": True, "show_window_on_start": True},
        "application": {"enable_auto_update": True, "auto_restart_on_error": False},
        "notification": {
            "enable_desktop_notification": True,
            "notify_authentication_request": True,
            "notify_device_connect": True,
            "notify_device_disconnect": False
        }
    }

    def get_settings(self):
        logger.info("get_settings")
        return self._settings

    def set_settings(self, settings):
        for key, value in settings.items():
            if key in self._settings and isinstance(value, dict):
                self._settings[key].update(value)
            else:
                self._settings[key] = value
        logger.info(f"set_settings")
        return True

class ReleaseApi:
    def get_current_application_version(self):
        # 仮実装
        return {"version": "v2.1.0"}

# --- API統合 ---
class Api:
    home = HomeApi()
    connect = ConnectApi()
    settings = SettingsApi()
    release = ReleaseApi()

