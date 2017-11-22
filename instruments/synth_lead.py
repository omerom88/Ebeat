from . import Instrument
from collections import deque
import mido
import numpy
import itertools
import operator

SCALE_WEIGHTS = [6, 2, 4, 2, 4, 1, 3]
MAX_JUMP = 7

EOLIAN_SCALE = [0, 2, 3, 5, 7, 8, 10]

class SynthLead(Instrument):
    TRACK_NAME_BASE = "Lead Synth"
    
    def __init__(self, live_set, role, recording_ended_callback):
        super(SynthLead, self).__init__(live_set, role, recording_ended_callback)
        self.pending_messages = deque()
        self.output_port = mido.open_output("IAC Driver Melody %s" % self.role)

    def set_volume(self, value):
        self.get_track().volume = value
    
    def tick(self, tick_count):
        super(SynthLead, self).tick(tick_count)
        
        if self.player and not self.pending_messages:
            melody = self.get_notes()
            #print "Generated melody:", melody
            self.pending_messages.extend(melody)
            
        if self.pending_messages:
            #print "SYNTH LEAD SENDING MESSAGES"
            messages = self.pending_messages.popleft()
            #print "Sending messages:", messages
            for message in messages:
                self.output_port.send(message)
        # print tick_count
        # if tick_count % 96 == 0:
        #     print "on"
        #     self.output_port.send(mido.Message("note_on", note=57))
        # elif tick_count % 96 == 48:
        #     print "off"
        #     self.output_port.send(mido.Message("note_off", note=57))
            
    def get_notes(self):
        if self.player.mean_joint_distance < 0.5:
            # No movement or almost no movement. Generate silent beat.
            return [[], [], [], []]
            
        # More motion = shorter note sequence & faster rhythm.
        # Movement value is normalized to range 0-1.
        normalized_mean_joint_distance = min((self.player.mean_joint_distance - 0.5) / 3, 1)
        inverse_mean_joint_distance = 1 - normalized_mean_joint_distance
        pattern_length_index = scale_to_range(inverse_mean_joint_distance, 0, 2)
        # Pattern can be [1, 2, 4] quarters long.
        pattern_length_beats = 2 ** pattern_length_index
        
        rh_y, lh_y, head_y, body_z, distance_between_hands = self.player.param_values
        number_of_notes = scale_to_range(distance_between_hands, 1, 12)
        # Shortest note is 16th note.
        if number_of_notes > pattern_length_beats * 4:
            number_of_notes = pattern_length_beats * 4
        
        rhythmic_pattern = self.choose_note_start_locations(pattern_length_beats, number_of_notes)
        # Lowest note in range corresponds to rh_y. A1 - A3.
        # Notes are numbered as "offset from A1".
        lowest_note = scale_to_range(rh_y, 0, 14)
        # Size of melody range corresponds to y distance between hands.
        note_range_size = scale_to_range(abs(rh_y - lh_y), 0, 7)
        # Melody start note corresponds to y position of left hand (offset from range start, in mode).
        melody_start = scale_to_range(lh_y, 0, note_range_size) + lowest_note
        pitches = self.get_melody_pitches(number_of_notes, note_range_size, lowest_note, melody_start)
        
        previous_start_location = 0
        previous_pitch = None
        previous_note_end = None
        messages = []
        midi_pitches = [self.get_midi_value(pitch) for pitch in pitches]
        melody_notes = deque(zip(rhythmic_pattern, midi_pitches))
        next_note_start, next_note_pitch = melody_notes.popleft()
        for tick in range(4 * pattern_length_beats):
            tick_messages = []
            if tick == next_note_start:
                tick_messages.append(mido.Message("note_on", note=next_note_pitch))
                # When starting a new note, end the previous one, if there is one still playing,
                # so that notes don't overlap.
                if previous_note_end:
                    tick_messages.append(mido.Message("note_off", note=previous_pitch))
                    previous_note_end = None
                    previous_pitch = None
                # Current note should end in 4 ticks maximum.
                previous_note_end = tick + 4
                previous_pitch = next_note_pitch
                # Advance to next note.
                if melody_notes:
                    next_note_start, next_note_pitch = melody_notes.popleft()
                else:
                    next_note_start = next_note_pitch = None
            elif tick == previous_note_end:
                tick_messages.append(mido.Message("note_off", note=previous_pitch))
                previous_pitch = None
                previous_note_end = None
                
            messages.append(tick_messages)
            
        return messages

    @staticmethod
    def get_midi_value(offset_from_a1):
        A1 = 57
        octave = itertools.count(0, 12)
        octave_offset = itertools.chain.from_iterable(itertools.repeat(item, 7) for item in octave)
        infinite_eolian = itertools.imap(operator.add, itertools.cycle(EOLIAN_SCALE), octave_offset)
        semitone_offset_from_a1 = next(itertools.islice(infinite_eolian, offset_from_a1, offset_from_a1 + 1))
        return A1 + semitone_offset_from_a1
        
    def choose_note_start_locations(self, pattern_length_beats, number_of_notes):
        weights = [1] * pattern_length_beats * 4
        for i in xrange(len(weights)):
            for power in xrange(1, 5):
                if i % (2 ** power) == 0:
                    weights[i] += 1
                    
        total = sum(weights)
        normalized_weights = [float(w) / total for w in weights]
        #print normalized_weights
        
        choices = numpy.random.choice(pattern_length_beats * 4, number_of_notes, False, normalized_weights)
        choices.sort()
        return choices
        
    
    def get_melody_pitches(self, number_of_notes, note_range_size, lowest_note, melody_start):
        current_note = melody_start
        highest_note = lowest_note + note_range_size
        pitches = []
        possible_notes = range(lowest_note, highest_note + 1)
        # note_scale_weights = [1] * len(possible_notes)
        # for i, note in range(len(possible_notes)):
        #     pitch_class = note % 7
        #     note_scale_weights[i] += self.SCALE_WEIGHTS[pitch_class]
            
        for i in xrange(number_of_notes):
            pitches.append(current_note)
            possible_next_notes = [
                i for i in xrange(current_note - MAX_JUMP, current_note + MAX_JUMP + 1)
                if lowest_note <= i <= highest_note
            ]
            next_note_weights = [0] * len(possible_next_notes)
            for i, note in enumerate(possible_next_notes):
                pitch_class = note % 7
                # Notes that are "strong" scale notes have a higher chance.
                weight = 2 * SCALE_WEIGHTS[pitch_class]
                # Notes that are far away have a lower chance.
                weight -= abs(current_note - note) 
                # No notes has no chance!
                weight = max(1, weight)
                next_note_weights[i] = weight
            #print "N:", possible_next_notes
            #print "W:", next_note_weights
            total = sum(next_note_weights)
            next_note_weights_normalized = [float(w) / total for w in next_note_weights]
            current_note = numpy.random.choice(possible_next_notes, p=next_note_weights_normalized)
    
        return pitches
    
def scale_to_range(value, min_value, max_value):
    """ Convert 0-1 value to value between min_value and max_value (inclusive) """
    scaled_value = min_value + int(value * (max_value - min_value + 1))
    return scaled_value if scaled_value <= max_value else max_value
