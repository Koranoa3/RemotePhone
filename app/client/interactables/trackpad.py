import ctypes
import math

MOUSE_SPEED_MULTIPLIER = 1
MOUSE_ACCELERATION = 1.2

def handle_event(event_type, data):
    if event_type == "tp_tap": # no args
        handle_tap()
    elif event_type == "tp_move": # dx, dy
        handle_move(data)
    elif event_type == "tp_scroll": # is_horiz, vol
        handle_scroll(data)
    else:
        print(f"Unknown event type: {event_type}")


def handle_tap():
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # Left button down
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # Left button up

def handle_move(data):
    dx = int(math.copysign(abs(float(data["dx"]) * MOUSE_SPEED_MULTIPLIER) ** MOUSE_ACCELERATION, data["dx"]))
    dy = int(math.copysign(abs(float(data["dy"]) * MOUSE_SPEED_MULTIPLIER) ** MOUSE_ACCELERATION, data["dy"]))
    ctypes.windll.user32.mouse_event(0x0001, dx, dy, 0, 0) # Move mouse

def handle_scroll(data):
    is_horiz = data["is_horiz"]
    vol = int(data["vol"])
    if is_horiz:
        # pyautogui.hscroll(vol)  # Horizontal scroll
        ctypes.windll.user32.mouse_event(0x1000, 0, 0, -vol, 0) # Horizontal scroll
    else:
        # pyautogui.vscroll(vol)  # Vertical scroll
        ctypes.windll.user32.mouse_event(0x0800, 0, 0, vol, 0) # Vertical scroll