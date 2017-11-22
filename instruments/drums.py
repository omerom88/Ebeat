from . import Instrument, Parameter

class Drums(Instrument):
    #CLIP_COUNT = 5
    TRACK_NAME_BASE = "Drums"
        
    def set_clip_based_parameter(self, track_name, value):
        track = self.get_track(track_name)
        max_clip_index = len(track.clips)
        clip_index = int(round(value * max_clip_index))
        if clip_index > 0:
            track.clips[clip_index - 1].play()
        else:
            track.stop()
    
    def tick(self, tick_count):
        super(Drums, self).tick(tick_count)
        
        if tick_count % 24 != 0 or not self.player:
            # Update only every beat
            return
        self.set_parameter1(self.player.param_values[1]) # Right hand
        self.set_parameter2(self.player.param_values[0]) # Left hand
        
    def set_parameter1(self, value):
        self.set_clip_based_parameter("Kick", value)
        self.set_clip_based_parameter("Clap", value)
        
    def set_parameter2(self, value):
        self.set_clip_based_parameter("Hihat", value)
        self.set_clip_based_parameter("Bongos", value)
        self.set_clip_based_parameter("Tambourine", value)

    def mute(self, muted):
        self.mute_on_tick = None
        muted = int(muted)
        track = self.get_track("0. Drums")
        print "Set muted for %s: %s" % (track.name, muted)
        self.live_set.set_track_mute(track.index, muted)

    _parameters = [
        #Parameter("base", set_base)
    ]
