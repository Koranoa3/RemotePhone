import ctypes
import json

from logging import getLogger
logger = getLogger(__name__)

from app.client.interactables.keycodes import (
    KEYEVENTF_KEYDOWN,
    KEYEVENTF_KEYUP,
    VK_MAP,
    NO_KEYUP_ACTIONS
)

def press_key(key_code):
    try:
        ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYDOWN, 0)
        ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)
    except Exception as e:
        logger.error(f"Error pressing key {key_code}: {e}")

def key_down(key_code):
    try:
        ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYDOWN, 0)
    except Exception as e:
        logger.error(f"Error key_down {key_code}: {e}")

def key_up(key_code):
    try:
        ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)
    except Exception as e:
        logger.error(f"Error key_up {key_code}: {e}")

def hotkey(key_codes:list):
    try:
        for key_code in key_codes:
            ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYDOWN, 0)
        for key_code in reversed(key_codes):
            ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)
    except Exception as e:
        logger.error(f"Error pressing hotkey {key_codes}: {e}")

def resolve_action(action):
    if isinstance(action, str) and (action.startswith("[") or action.startswith("{")):
        try:
            action = json.loads(action)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON action: {e}")

    if isinstance(action, list):
        result = []
        for a in action:
            resolved = VK_MAP.get(a, a if isinstance(a, int) else None)
            if isinstance(resolved, list):
                result.extend(resolved)
            elif isinstance(resolved, int):
                result.append(resolved)
            else:
                logger.warning(f"Unknown action element: {a}")
                return None
        return result
    elif isinstance(action, str):
        resolved = VK_MAP.get(action, None)
        if isinstance(resolved, list):
            return resolved
        elif isinstance(resolved, int):
            return [resolved]
        else:
            logger.warning(f"Unknown action: {action}")
            return None
    elif isinstance(action, int):
        return [action]
    else:
        logger.warning(f"Invalid action type: {action}")
        return None


def handle_action(data):
    action = data.get("action", None)
    if action is None:
        logger.warning(f"Invalid command: {action}")
        return "Invalid"

    pressure = data.get("pressure", "press") # "press" / "down" / "up"
    key_codes = resolve_action(action)
    if key_codes is None:
        return "Invalid"

    if pressure == "down":
        for code in key_codes:
            key_down(code)
    elif pressure == "up":
        for code in key_codes:
            if code not in NO_KEYUP_ACTIONS:
                key_up(code)
    elif pressure == "press":
        hotkey(key_codes)
    else:
        logger.warning(f"Invalid pressure value: {pressure}")
