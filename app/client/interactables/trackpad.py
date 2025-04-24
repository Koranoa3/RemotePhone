import ctypes
import math

from logging import getLogger
logger = getLogger(__name__)

def handle_event(event_type, data):
    if event_type == "tp_tap": # no args
        handle_tap()
    elif event_type == "tp_move": # dx, dy
        handle_move(data)
    elif event_type == "tp_scroll": # is_horiz, delta
        handle_scroll(data)
    else:
        logger.warning(f"Unknown event type: {event_type}")


def handle_tap():
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # Left button down
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # Left button up

def handle_move(data):
    dx = int(data["dx"])
    dy = int(data["dy"])
    ctypes.windll.user32.mouse_event(0x0001, dx, dy, 0, 0) # Move mouse

def handle_scroll(data):
    is_horiz = data.get("is_horiz", False)
    delta = int(data["delta"])
    if is_horiz:
        # pyautogui.hscroll(delta)  # Horizontal scroll
        ctypes.windll.user32.mouse_event(0x1000, 0, 0, -delta, 0) # Horizontal scroll
    else:
        # pyautogui.vscroll(delta)  # Vertical scroll
        ctypes.windll.user32.mouse_event(0x0800, 0, 0, -delta, 0) # Vertical scroll