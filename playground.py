import live
from instruments.drums import Drums

live_set = live.Set()
#live_set.live.cmd("/remix/set_peer", "10.0.0.1", 9001)

live_set.scan(scan_clip_names=True, scan_devices=True)
drums = Drums(live_set)
