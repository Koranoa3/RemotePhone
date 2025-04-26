import ctypes

from logging import getLogger
logger = getLogger(__name__)

BUTTONS_DOWN = {
    "left": 0x0002,
    "right": 0x0008,
    "middle": 0x0020,
}
BUTTONS_UP = {
    "left": 0x0004,
    "right": 0x0010,
    "middle": 0x0040,
}


def handle_event(event_type, data):
    if event_type == "tp_tap": # pressure, button
        handle_tap(data)
    elif event_type == "tp_move": # dx, dy
        handle_move(data)
    elif event_type == "tp_scroll": # is_horiz, delta
        handle_scroll(data)
    else:
        logger.warning(f"Unknown event type: {event_type}")


def handle_tap(data):
    pressure = data.get("pressure", "click") # click / up / down
    button = data.get("button", "left") # left / right / middle
    
    if button not in BUTTONS_DOWN:
        logger.warning(f"Unknown button: {button}")
        return    
    
    if pressure == "click":
        ctypes.windll.user32.mouse_event(BUTTONS_DOWN[button], 0, 0, 0, 0)  # Button down
        ctypes.windll.user32.mouse_event(BUTTONS_UP[button], 0, 0, 0, 0)    # Button up
    elif pressure == "down":
        ctypes.windll.user32.mouse_event(BUTTONS_DOWN[button], 0, 0, 0, 0)
    elif pressure == "up":
        ctypes.windll.user32.mouse_event(BUTTONS_UP[button], 0, 0, 0, 0)
    else:
        logger.warning(f"Unknown pressure state: {pressure}")


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