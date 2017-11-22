import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
import live
from instruments.drums import Drums
from instruments.synth_lead import SynthLead
from instruments.synth_harmony import SynthHarmony
from kinect import KinectInterface
from threading import Thread
import time

def start_kinect_tracking():
    global kinect
    kinect = KinectInterface()
    try:
        kinect.start()
    except KeyboardInterrupt:
        return

def start_ableton_thread():
    t = Thread(target=ableton_thread)
    t.start()

def ableton_thread():
    live_set = live.Set()
    live_set.scan(scan_clip_names=True, scan_devices=True)
    drums = Drums(live_set)
    melody = SynthLead(live_set)
    harmony = SynthHarmony(live_set)
    while True:
        time.sleep(0.1)
        right_hand, left_hand, head_height, body_depth = kinect.param_values
        print "Params: (%.3f, %.3f, %.3f, %.3f)" % kinect.param_values
        drums.set_parameter1(right_hand)
        drums.set_parameter2(left_hand)

        melody.set_volume(1 - head_height)
        harmony.set_volume(1 - body_depth)

def main():
    start_ableton_thread()
    # This runs the kinect loop until Ctrl+C
    start_kinect_tracking()
    return



if __name__ == "__main__":
    main()
