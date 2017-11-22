import sys
import live
from instruments.drums import Drums
from instruments.synth_lead import SynthLead
from instruments.synth_harmony import SynthHarmony
from threading import Thread
import time
import mido

# def start_ableton_thread():
#     t = Thread(target=ableton_thread)
#     t.start()
 
def ableton_thread():
    live_set = live.Set()
    live_set.scan(scan_clip_names=True, scan_devices=True)
    beat_length = 60 / live_set.tempo 
    # drums = Drums(live_set)
    melody = SynthLead(live_set)
    # harmony = SynthHarmony(live_set)
    melody_output = mido.open_output("IAC Driver Bus 1")
    clock_input = mido.open_input("IAC Driver IAC Bus 2")
    tick_count = 0
    for message in clock_input:
        if message.type == "clock":
            tick_count += 1
            if tick_count % 24 == 0:
                melody_output.send(mido.Message("note_on", note=60, velocity=tick_count % 96 + 10))
            elif tick_count % 12 == 0:
                melody_output.send(mido.Message("note_off", note=60))
        elif message.type == "start":
            tick_count = 0
    # while True:
    #     live_set.wait_for_next_beat()
    #     print "Beat"
    #     melody_output.send(mido.Message("note_on", note=60, velocity=64))
    #     time.sleep(beat_length / 2)
    #     melody_output.send(mido.Message("note_off", note=60))

def main():
    ableton_thread()
    
if __name__ == "__main__":
    main()
