"""
available key codes for Windows

a~z, 0=9, F1~F24, numpad0~9, lbutton, rbutton, mbutton, back, tab,
return, shift, control, menu, up, down, left, right, media*, volume*...

not included: +*:;<>-=^~\/_[]{}#@!%&`"'
"""

import win32con

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002

# 仮想キー名のマップを自動生成（VK_接頭辞を除いてlower変換）
VK_MAP = {
    name[3:].lower(): value
    for name, value in vars(win32con).items()
    if name.startswith("VK_")
}
VK_MAP.update({
    "win": VK_MAP["lwin"],
    "windows": VK_MAP["lwin"],
    "esc": VK_MAP["escape"],
    "ret": VK_MAP["return"],
    "del": VK_MAP["delete"],
    "ctrl": VK_MAP["control"],
    "alt": VK_MAP["menu"],  # alt
    "bksp": VK_MAP["back"],
    
    "prev_virtual_desktop": [win32con.VK_LCONTROL, win32con.VK_LWIN, win32con.VK_LEFT],
    "next_virtual_desktop": [win32con.VK_LCONTROL, win32con.VK_LWIN, win32con.VK_RIGHT],
    
})
# A-Z
VK_MAP.update({chr(i).lower(): i for i in range(0x41, 0x5B)})
# 0-9
VK_MAP.update({chr(i): i for i in range(0x30, 0x3A)})

NO_KEYUP_ACTIONS = [
    VK_MAP["volume_mute"],
    VK_MAP["volume_up"],
    VK_MAP["volume_down"],
    VK_MAP["media_play_pause"],
    VK_MAP["media_next_track"],
    VK_MAP["media_prev_track"],
]

# note: +*:;-=等のコードは含まれない 代わりにキーではなく文字として入力させること

if __name__ == "__main__":
    # テスト用: マップの内容を表示
    for key, value in VK_MAP.items():
        print(f"{key}: {value}")