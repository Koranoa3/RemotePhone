from app.host import host_config
from app.host import version

from logging import getLogger
logger = getLogger(__name__)


# --- API classes ---
class HomeApi:
    def get_device_connection_status(self):
        # 仮実装
        return {
            "status": "connected",  # or "not connected"
            "device_name": "iPhone 15 Pro",
            "rtt": "25ms",
            "rtt_status": "stable",
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
        return {"version": version.get_installed_version()}

    def get_current_version_info(self):
        current_release = version.get_installed_release()
        return {
            "version": current_release.get_version(),
            "released_at": current_release.get_released_at(),
            "release_notes": current_release.get_release_note()
        }

    def check_for_updates(self):
        current_release = version.get_installed_release()
        logger.debug(f"Current release: {current_release.get_version()}")
        if current_release.is_latest():
            return {"update_available": False}

        latest_version = version.get_latest_version()
        latest_release = version.get_release(latest_version)
        return {
            "update_available": True,
            "version": latest_release.get_version(),
            "released_at": latest_release.get_released_at(),
            "release_notes": latest_release.get_release_note()
        }
    
    def update_now(self):
        # 仮実装
        logger.info("update_now called")
        return True

# --- API integration ---
class Api:
    home = HomeApi()
    connect = ConnectApi()
    settings = SettingsApi()
    release = ReleaseApi()

