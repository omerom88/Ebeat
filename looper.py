import live
from instruments.drums import Drums

class AbletonLooper(object):
    #TRACKS = [Drums, Synth,]
    METER = 4
    BARS_IN_LOOP = 4

    def __init__(self):
        self.recording_track = []
        
    def start(self):
        """
        Start counting time.
        """
        pass

    def start_loop_recording(self, track):
        """
        Wait until the next loop start time, and start recording a loop on the specified track,
        overriding any existing content in that track. Recording ends when the length of the loop is
        finished. Recording overrides any existing content in the track.
        """
        pass
        
    def mute_track(self, track, muted):
        """
        Mute or unmute a track.
        """
        pass

    def set_parameter_value(self, parameter, value):
        """
        Set value of specified parameter on the currently recording track, given parameter id (1-4) and
        value (float between 0 and 1).
        """
        pass


def main():
    live_set = live.Set()
    live_set.scan(scan_clip_names=True, scan_devices=True)
    drums = Drums(live_set)
    drums.set_base(0.2)
    
    
if __name__ == "__main__":
    main()
