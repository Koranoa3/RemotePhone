import os, json
import requests

from app.common import resource_path
VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/"

class Version:
    
    @staticmethod
    def get_current() -> dict:
        """
        
        """
        if Version.is_latest():
            return Version.get_latest()
        
        version = Version.get_current_version()
        current_path = resource_path("app/resources/current_release.json")
        current_json = None

        if os.path.exists(current_path):
            try:
                with open(current_path, "r", encoding="utf-8") as f:
                    current_json = json.load(f)
                saved_version = current_json.get("version")
                if saved_version == version:
                    return current_json
            except Exception as e:
                print(f"[Error] Failed to read current_release.json: {e}")

        # Fetch from server if version differs or file does not exist
        try:
            res = requests.get(VERSION_INFO_URL + version, timeout=5)
            res.raise_for_status()
            current_json = res.json()
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, "w", encoding="utf-8") as f:
                json.dump(current_json, f, ensure_ascii=False, indent=2)
            return current_json
        except Exception as e:
            print(f"[Error] Failed to fetch or save the current version info: {e}")
            return None


    @staticmethod
    def get_current_version() -> str:
        """
        
        """
        try:
            with open(resource_path("app/resources/version"), "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "unknown"
        except Exception as e:
            return "unknown"

    @staticmethod
    def get_latest() -> dict:
        """
        
        """
        latest_path = resource_path("app/resources/latest_release.json")
        current_version = Version.get_current_version()
        latest_json = None

        if os.path.exists(latest_path):
            try:
                with open(latest_path, "r", encoding="utf-8") as f:
                    latest_json = json.load(f)
                latest_version = latest_json.get("version")
                if latest_version == current_version:
                    return latest_json
            except Exception as e:
                print(f"[Error] Failed to read latest_release.json: {e}")

        # Fetch from server if version differs or file does not exist
        try:
            res = requests.get(VERSION_INFO_URL + "latest", timeout=5)
            res.raise_for_status()
            latest_json = res.json()
            os.makedirs(os.path.dirname(latest_path), exist_ok=True)
            with open(latest_path, "w", encoding="utf-8") as f:
                json.dump(latest_json, f, ensure_ascii=False, indent=2)
            return latest_json
        except Exception as e:
            print(f"[Error] Failed to fetch or save the latest version info: {e}")
            return None

    @staticmethod
    def get_latest_version() -> str:
        """
        
        """
        latest_json = Version.get_latest()
        if latest_json and isinstance(latest_json, dict):
            return latest_json.get("version")
        return None

    @staticmethod
    def get_latest_release_notes() -> str:
        """
        
        """
        latest_json = Version.get_latest()
        if latest_json and isinstance(latest_json, dict):
            return latest_json.get("release_notes")
        return None

    @staticmethod
    def is_latest() -> bool:
        """
        
        """
        current_version = Version.get_current_version()
        latest_version = Version.get_latest_version()
        return current_version == latest_version if latest_version else False