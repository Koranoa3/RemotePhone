from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# 初期化：一度だけ呼ぶ
def init_volume_controller():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume

# 音量を変化させる（相対変化）
def change_volume(volume_ctrl, delta: float):
    current = volume_ctrl.GetMasterVolumeLevelScalar()
    new_volume = min(1.0, max(0.0, current + delta))
    volume_ctrl.SetMasterVolumeLevelScalar(new_volume, None)
    return new_volume

def get_volume(volume_ctrl):
    return volume_ctrl.GetMasterVolumeLevelScalar()

def set_volume(volume_ctrl, volume: float):
    volume = min(1.0, max(0.0, volume))
    volume_ctrl.SetMasterVolumeLevelScalar(volume, None)
    return volume