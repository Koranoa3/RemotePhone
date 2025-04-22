from client.interactables import volume_controller as vc

volume_ctrl = vc.init_volume_controller()

def handle_event(event_type, data):
    if event_type == "volume_up": # no args
        vc.change_volume(volume_ctrl, +0.05)
    elif event_type == "volume_down": # no args
        vc.change_volume(volume_ctrl, -0.05)
    elif event_type == "volume_change": # delta
        vc.change_volume(volume_ctrl, float(data["delta"])/100)
    elif event_type == "volume_set": # volume
        vc.set_volume(volume_ctrl, float(data["volume"]))