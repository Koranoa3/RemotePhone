import os, sys, json
import requests

VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest"

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class Version:
    
    def get_current() -> dict:
        """
        
        """
        version = Version.get_current_version()
        return {
            "version": version,
            "released_at": "unknown",
            "release_notes": "No release notes available"
        }
    
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
        latest_path = resource_path("app/resources/latest.json")
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
                print(f"[Error] Failed to read latest.json: {e}")

        # Fetch from server if version differs or file does not exist
        try:
            res = requests.get(VERSION_INFO_URL, timeout=5)
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
