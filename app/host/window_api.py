from app.host import host_config

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
    def get_settings(self):
        logger.debug("get_settings")
        return host_config.load()

    def set_settings(self, settings):
        current_settings = host_config.load()
        for key, value in settings.items():
            if key in current_settings and isinstance(value, dict):
                current_settings[key].update(value)
            else:
                current_settings[key] = value
        host_config.save(current_settings)
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

