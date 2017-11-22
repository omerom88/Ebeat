from . import Instrument, Parameter
from synth_lead import scale_to_range

class SynthHarmony(Instrument):
    TRACK_NAME_BASE = "Stab Synth"
    
    def tick(self, tick_count):
        super(SynthHarmony, self).tick(tick_count)
        # if self.role == 1 and tick_count % 24*4 == 0:
        #     print "Role 1. Player:", self.player
        #print "SYNTH HARMONY TICK", self.role, self.player
        if not self.player or self.tick_count % 24 != 0:
            return
        #self.set_volume(self.player.param_values[3]) # Body z position
        lh_y, rh_y, head_y, body_z, hand_dist = self.player.param_values
        # Set device parameters of "Beat Repeat": grid, pitch decay, (interval, variation)
        track = self.get_track()
        beat_repeat = self.get_device_named("Beat Repeat")
        grid = beat_repeat.parameters[4] # Parameter range is 0-15, we want only 6-15.
        pitch_decay = beat_repeat.parameters[10] # Parameter range 0-1
        variation = beat_repeat.parameters[6] # Parameter range 0-10
        offset = beat_repeat.parameters[3] # Parameter range 0-15.
        
        pitch_decay.set_value(1 - head_y) # Low head = maximum pitch decay
        grid.set_value(scale_to_range(1 - hand_dist, 6, 15)) # Far away hands = smaller grid
        variation.set_value(scale_to_range(1 - body_z, 0, 10)) # Closer to Kinect = more variation
        offset.set_value(scale_to_range(lh_y, 0, 15)) # Higher left hand - larger offset

        # [(0, 'Device On'),
        #  (1, 'Chance'),
        #  (2, 'Interval'),
        #  (3, 'Offset'),
        #  (4, 'Grid'),
        #  (5, 'Block Triplets'),
        #  (6, 'Variation'),
        #  (7, 'Variation Type'),
        #  (8, 'Gate'),
        #  (9, 'Decay'),
        #  (10, 'Pitch Decay'),
        #  (11, 'Pitch'),
        #  (12, 'Mix Type'),
        #  (13, 'Volume'),
        #  (14, 'Filter On'),
        #  (15, 'Filter Freq'),
        #  (16, 'Filter Width'),
        #  (17, 'Repeat')]

        
    def set_volume(self, value):
        self.get_track().volume = value
