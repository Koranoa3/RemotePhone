from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize

# Initialization: Call this only once
def get_volume_controller():
    CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

# Change volume (relative change)
def change_volume(delta: float):
    current = volume_ctrl.GetMasterVolumeLevelScalar()
    new_volume = min(1.0, max(0.0, current + delta))
    volume_ctrl.SetMasterVolumeLevelScalar(new_volume, None)
    return new_volume

def get_volume():
    return volume_ctrl.GetMasterVolumeLevelScalar()

def set_volume(volume: float):
    volume = min(1.0, max(0.0, volume))
    volume_ctrl.SetMasterVolumeLevelScalar(volume, None)
    return volume

# Periodically check and reinitialize if needed
def refresh_volume_controller_if_needed():
    global volume_ctrl, prev_id
    CoInitialize()
    current = AudioUtilities.GetSpeakers()
    if current.GetId() != prev_id:
        volume_ctrl = get_volume_controller()
        prev_id = current.GetId()

# On startup
volume_ctrl = get_volume_controller()
prev_id = AudioUtilities.GetSpeakers().GetId()