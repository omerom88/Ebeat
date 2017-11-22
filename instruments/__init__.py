from collections import namedtuple

class Instrument(object):
    # Override this
    TRACK_NAME_BASE = None
    
    def __init__(self, live_set, role, recording_ended_callback):
        self.live_set = live_set
        self.role = role
        self.player = None
        self.next_record_slot = 0
        self.tick_count = 0
        self.recording_stop_tick_count = None
        self.recording_ended_callback = recording_ended_callback
        self.is_recording = False
        self.mute_on_tick = None
        
    def get_track_named(self, name):
    	""" Returns the Track with the specified name, or None if not found. """
    	for track in self.live_set.tracks:
    		if track.name == name:
    			return track
    	raise KeyError(name)
        
    def get_device_named(self, name, track=None):
        track = track or self.get_track()
    	for device in track.devices:
    		if device.name == name:
    			return device
    	raise KeyError(name)
        
    def get_track_name(self, base_name=None):
        base_name = base_name or self.TRACK_NAME_BASE
        return "%s %s" % (base_name, self.role)
        
    def get_track(self, base_name=None):
        return self.get_track_named(self.get_track_name(base_name))
    
    def get_recording_track(self, base_name=None):
        return self.get_track_named(self.get_track_name(base_name) + " Recording")
        
    def tick(self, tick_count):
        self.tick_count = tick_count
        if self.recording_stop_tick_count is not None and tick_count >= self.recording_stop_tick_count:
            self.stop_recording()
            
        if self.mute_on_tick is not None and tick_count >= self.mute_on_tick:
            self.mute(True)
        
    def start_recording(self):
        if self.is_recording:
            print "Instrument is already recording."
            return
        
        self.is_recording = True
        recording_track = self.get_recording_track()
        self.live_set.play_clip(recording_track.index, self.next_record_slot)
        self.next_record_slot += 1
        # Stop the recording after 4 bars (Ableton will wait until the beginning of the next bar).
        self.recording_stop_tick_count = self.tick_count + 24 * 4 * 4
        

    def stop_recording(self):
        self.is_recording = False
        print "Stopping recording for instrument %s, role %s" % (type(self).__name__, self.role)
        recording_track = self.get_recording_track()
        self.recording_stop_tick_count = None
        # Play the clip again. It will stop recording and start playing back the loop.
        self.live_set.play_clip(recording_track.index, self.next_record_slot - 1)
        self.recording_ended_callback(self.role)
    
    def mute(self, muted):
        self.mute_on_tick = None
        muted = int(muted)
        track = self.get_track()
        print "Set muted for %s: %s" % (track.name, muted)
        track.set_mute(muted)
        
    def activate(self):
        self.mute(False)
        self.get_recording_track().stop()
        
    def deactivate(self):
        # Wait for next beat to mute the track
        self.mute_on_tick = 24 * (self.tick_count / 24 + 1)
        
Parameter = namedtuple("Parameter", ("name", "set_value_func",))
