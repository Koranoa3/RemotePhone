from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize

# 初期化：一度だけ呼ぶ
def get_volume_controller():
    CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

# 音量を変化させる（相対変化）
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

# 周期的にチェックして再取得
def refresh_volume_controller_if_needed():
    global volume_ctrl, prev_id
    CoInitialize()
    current = AudioUtilities.GetSpeakers()
    if current.GetId() != prev_id:
        print("🔄 出力デバイスが変わったので再取得します")
        volume_ctrl = get_volume_controller()
        prev_id = current.GetId()

# 起動時
volume_ctrl = get_volume_controller()
prev_id = AudioUtilities.GetSpeakers().GetId()