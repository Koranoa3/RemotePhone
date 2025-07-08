import os, sys
import winreg

from logging import getLogger
logger = getLogger(__name__)

def app_path(relative_path: str) -> str:
    """
    Resolves the absolute path to an application resource, handling edge cases like missing files or incorrect paths.

    Args:
        relative_path (str): The relative path to the application resource.

    Returns:
        str: The absolute path to the application resource, or None if the path is invalid.
    """
    try:
        base_path = os.path.abspath(".")
        path = os.path.join(base_path, relative_path)
        if not os.path.exists(path):
            logger.warning(f"Application resource not found: {path}")
        return path
    except Exception as e:
        logger.error(f"Error resolving application path for {relative_path}: {e}")
        return None

def app_resource_path(relative_path: str) -> str:
    """
    Resolves the absolute path to a resource, handling edge cases like missing files or incorrect paths.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource, or None if the path is invalid.
    """
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        path = os.path.join(base_path, "app", "resources", relative_path)
        if not os.path.exists(path):
            logger.warning(f"Resource not found: {path}")
        return path
    except Exception as e:
        logger.error(f"Error resolving resource path for {relative_path}: {e}")
        return None

# PCのデバイスID（Windows: MachineGuid）を取得
def get_device_id():
    if os.name == "nt": # Windows
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            return value
        except Exception:
            return "unknown"
    else:
        return "unknown"
