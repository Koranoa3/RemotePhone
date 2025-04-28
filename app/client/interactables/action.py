import win32con, ctypes
import json

from logging import getLogger
logger = getLogger(__name__)

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002

ACTIONS = {
    "volume_up": win32con.VK_VOLUME_UP,
    "volume_down": win32con.VK_VOLUME_DOWN,
    "play_pause": win32con.VK_MEDIA_PLAY_PAUSE,
    "next_track": win32con.VK_MEDIA_NEXT_TRACK,
    "prev_track": win32con.VK_MEDIA_PREV_TRACK,
    "mute": win32con.VK_VOLUME_MUTE,

    "prev_virtual_desktop": [win32con.VK_LCONTROL, win32con.VK_LWIN, win32con.VK_LEFT],
    "next_virtual_desktop": [win32con.VK_LCONTROL, win32con.VK_LWIN, win32con.VK_RIGHT],
    "screenshot": win32con.VK_SNAPSHOT,

    "win": win32con.VK_LWIN,
    "esc": win32con.VK_ESCAPE,
    "enter": win32con.VK_RETURN,
    "space": win32con.VK_SPACE,
    "backspace": win32con.VK_BACK,
    "delete": win32con.VK_DELETE,
    "tab": win32con.VK_TAB,
    "ctrl": win32con.VK_LCONTROL,
    "shift": win32con.VK_LSHIFT,
    "alt": win32con.VK_LMENU,

    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
}
NO_KEYUP_ACTIONS = [
    win32con.VK_VOLUME_UP,
    win32con.VK_VOLUME_DOWN,
    win32con.VK_MEDIA_PLAY_PAUSE,
    win32con.VK_MEDIA_NEXT_TRACK,
    win32con.VK_MEDIA_PREV_TRACK,
    win32con.VK_VOLUME_MUTE,
]

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
    if isinstance(action, list):
        result = []
        for a in action:
            resolved = ACTIONS.get(a, a if isinstance(a, int) else None)
            if isinstance(resolved, list):
                result.extend(resolved)
            elif isinstance(resolved, int):
                result.append(resolved)
            else:
                logger.warning(f"Unknown action element: {a}")
                return None
        return result
    elif isinstance(action, str):
        resolved = ACTIONS.get(action, None)
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
        return

    pressure = data.get("pressure", "press") # "press" / "down" / "up"
    key_codes = resolve_action(action)
    if key_codes is None:
        return

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


def handle_vk(data):
    key_code = data.get("vk", None)
    if key_code is None:
        logger.warning(f"Invalid command: no 'vk' argument?")
        return
    
    key_code = json.loads(key_code)
    pressure = data.get("pressure", "press") # "press" / "down" / "up"

    if isinstance(key_code, list):
        if not pressure == "up":
            hotkey(key_code)
    elif isinstance(key_code, int):
        if pressure == "down":
            key_down(key_code)
        elif pressure == "up":
            key_up(key_code)
        else:
            press_key(key_code) 
           
    else:
        logger.warning(f"Unknown VirtualKey command: {key_code}")
        return