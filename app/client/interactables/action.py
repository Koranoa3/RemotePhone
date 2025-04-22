import win32con, ctypes

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
}

def press_key(key_code):
    try:
        ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYDOWN, 0)
        ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"Error pressing key {key_code}: {e}")

def hotkey(key_codes:list):
    try:
        for key_code in key_codes:
            ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYDOWN, 0)
        for key_code in reversed(key_codes):
            ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"Error pressing hotkey {key_codes}: {e}")

def handle_event(data):
    action = data.get("action", None)
    if action is None or type(action) != str:
        print(f"Invalid command: {action}")
        return

    key_code = ACTIONS.get(action, None)
    if key_code:

        if isinstance(key_code, list):
            hotkey(key_code)
        else:
            press_key(key_code)
        
    else:
        print(f"Unknown action command: {action}")
        return