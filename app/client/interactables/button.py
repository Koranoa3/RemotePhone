import ctypes
import win32con
import json

from logging import getLogger
logger = getLogger(__name__)

# 拡張ボタンのコード
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002

BUTTON_MAP = {
    "left": {
        "down": win32con.MOUSEEVENTF_LEFTDOWN,
        "up": win32con.MOUSEEVENTF_LEFTUP
    },
    "right": {
        "down": win32con.MOUSEEVENTF_RIGHTDOWN,
        "up": win32con.MOUSEEVENTF_RIGHTUP
    },
    "middle": {
        "down": win32con.MOUSEEVENTF_MIDDLEDOWN,
        "up": win32con.MOUSEEVENTF_MIDDLEUP
    },
    "x1": {
        "down": win32con.MOUSEEVENTF_XDOWN,
        "up": win32con.MOUSEEVENTF_XUP,
        "data": XBUTTON1
    },
    "x2": {
        "down": win32con.MOUSEEVENTF_XDOWN,
        "up": win32con.MOUSEEVENTF_XUP,
        "data": XBUTTON2
    }
}

def mouse_button_event(button, pressure):
    button = button.lower()
    pressure = pressure.lower()

    if button not in BUTTON_MAP:
        logger.warning(f"Unknown mouse button: {button}")
        return

    event_flag = BUTTON_MAP[button].get(pressure)
    if not event_flag:
        logger.warning(f"Invalid pressure for mouse button: {pressure}")
        return

    data = BUTTON_MAP[button].get("data", 0)

    try:
        ctypes.windll.user32.mouse_event(event_flag, 0, 0, data, 0)
    except Exception as e:
        logger.error(f"Error sending mouse event {button}-{pressure}: {e}")

def handle_mousebutton(data):
    button = data.get("button")
    pressure = data.get("pressure")  # "down" / "up"

    if not button or not pressure:
        logger.warning(f"Invalid mouse command: {data}")
        return

    if pressure == "down":
        mouse_button_event(button, "down")
    elif pressure == "up":
        mouse_button_event(button, "up")
    else:
        logger.warning(f"Unknown pressure value: {pressure}")
