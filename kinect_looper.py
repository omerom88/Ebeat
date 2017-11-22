import os
import sys
import live
from instruments.drums import Drums
from instruments.synth_lead import SynthLead, scale_to_range
from instruments.synth_harmony import SynthHarmony
from threading import Thread, Event
import time
import mido
from primesense import nite2
from kinect import KinectInterface, UserRole
import signal
import graphics
import pyglet
import traceback

class KinectLooper(object):
    def __init__(self):
        # TODO: add callback for user lost, to remove 'player' from instruments.
        self.kinect = KinectInterface(self.gesture_received, self.pose_detected, self.user_added, self.user_removed, self.user_roles_changed)
        self.ableton_thread_stop_event = Event()
        self.ableton_thread_exited_event = Event()
        
    def start(self):
        self.start_ableton_thread()
        self.kinect.start()
        
    def start_ableton_thread(self):
        is_running = os.system("ps axc -o command  | grep -q ^Live$") == 0
        if not is_running:
            raise RuntimeError("Please run Abelton and open the Looper project")
        print "Initializing Ableton connection"
        # Initialization is done on the main thread.
        self.live_set = live.Set()
        # Patch pylive's console dumping.
        self.live_set.dump = lambda *args: None
        self.live_set.scan(scan_clip_names=True, scan_devices=True)
        
        print "Setting up Ableton session"
        assert self.live_set.tempo == 120, "Tempo must be 120"
        assert len(self.live_set.tracks) == 23, (
            "Didn't find all tracks, make sure you have the right file opened "
            "and that groups are expanded in Ableton!"
        )
        for track in self.live_set.group_named("0. Recordings").tracks:
            assert len(track.clips) == 0, (
                "Found clips in track '%s', "
                "please delete all 'Recording' clips in Ableton" % track.name
            )
        for track in self.live_set.tracks:
            self.live_set.set_track_mute(track.index, 0)
            track.stop()
        self.live_set.stop()
        self.live_set.time = 0
        for track_to_play in ("Stab Synth 1", "Stab Synth 2"):
            track = self.get_track_named(track_to_play)
            # track.volume = 0
            track.mute = 1
            track.clips[0].play()
        
        
        self.beat_length = 60 / self.live_set.tempo 
        
        self.user_tracks = {}
        self.active_tracks = {}
        for role in (UserRole.RIGHT_USER, UserRole.LEFT_USER):
            self.user_tracks[role] = {
                Track.MELODY: SynthLead(self.live_set, role, self.recording_ended),
                Track.HARMONY: SynthHarmony(self.live_set, role, self.recording_ended),
                Track.DRUMS: Drums(self.live_set, role, self.recording_ended)
            }
            self.active_tracks[role] = None

        self.ableton_thread = Thread(target=self.ableton_thread_func)
        self.ableton_thread.daemon = True
        self.ableton_thread.start()

    def ableton_thread_func(self):
        try:
            self.midi_clock_loop()
        except:
            print "Caught exception in Ableton thread"
            traceback.print_exc()
            print "Exiting Pyglet app from Ableton thread"
            pyglet.app.exit()
        finally:
            self.live_set.stop()
            print "Ableton thread setting exit event"
            self.ableton_thread_exited_event.set()
        
    def midi_clock_loop(self):
        clock_input = mido.open_input("IAC Driver Clock")
        
        tick_count = 0
        # MIDI clock loop - 24 times in each beats
        # For 130 BPM, beat_length=6/13sec, so MIDI clock tick is every 1/52sec =~ 19.23ms.
        # One 1/16 note = 4 clock ticks =~ 80ms.
        for message in clock_input:
            if self.ableton_thread_stop_event.is_set():
                print "Ableton thread received exit signal"
                return
                
            if message.type == "start":
                tick_count = 0
            elif message.type == "clock":
                tick_count += 1
                if tick_count % 6 == 0:
                    #print "1/16 tick"
                    # We only update every sixteenth note (~80ms).
                    self.midi_tick(tick_count)
                    
                if tick_count % (24 * 8) == 0:
                    self.log_status()
            
    def midi_tick(self, tick_count):
        for user_tracks in self.user_tracks.values():
            for track in user_tracks.values():
                track.tick(tick_count)
    
    def log_status(self):
        try:
            print "Tracked users:", [
                "id: %s, role: %s" % (user_id, user.role) \
                for user_id, user in self.kinect.user_listener.tracked_users.items()
            ]
            print "Active tracks:", self.active_tracks
        except:
            pass
        
    def gesture_received(self, user_id, hand, gesture):
        if gesture.type == nite2.c_api.NiteGestureType.NITE_GESTURE_CLICK:
            user = self.kinect.user_listener.tracked_users[user_id]
            if hand == nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HAND:
                other_hand_angle = user.lh_angle
            else:
                other_hand_angle = user.rh_angle
                
            if other_hand_angle < 70:
                track = Track.MELODY
            elif other_hand_angle < 110:
                track = Track.HARMONY
            else:
                track = Track.DRUMS
            print "Other hand angle is:", other_hand_angle
            # TODO: Disabled for now - use for "effects" mode
            #self.activate_track(user_id, track)
    
    def activate_track(self, user_id, track):
        user = self.kinect.user_listener.tracked_users[user_id]
        role = user.role
        if role not in self.active_tracks:
            print "Tried to activate track %s for user %s but user's role %s doesn't have active track" % (track, user_id, role)
            return
        previous_track = self.active_tracks[role]
        if previous_track == track:
            print "Tried to activate track %s for user %s but it's already active" % (track, user_id)
            return
        
        print "Activating track %s for user %s (previous track: %s)" % (track, user_id, previous_track)
        self.active_tracks[role] = track
        if previous_track is not None:
            self.user_tracks[user.role][previous_track].deactivate()
            self.user_tracks[user.role][previous_track].player = None
        if track is not None:
            track = self.user_tracks[user.role][track]
            print "Set track! track=%s, user=%s" % (track, user)
            track.player = user
            track.activate()
            
    def pose_detected(self, user_id, pose):
        if pose == nite2.c_api.NitePoseType.NITE_POSE_PSI:
            user = self.kinect.user_listener.tracked_users.get(user_id)
            if not user:
                print "user_id %s doesn't exist yet in tracked_users, ignoring" % user_id
                return
                
            active_track = self.active_tracks[user.role]
            if active_track is None:
                print "Detected PSI for %s but no track is active" % user_id
                return
            print "Starting to record for role %s track %s" % (user.role, active_track)
            instrument = self.user_tracks[user.role][active_track]
            instrument.start_recording()
        
    def user_roles_changed(self, changed_user_id):
        print "User roles changed! New roles:", [
            (user_id, user.role) for user_id, user
            in self.kinect.user_listener.tracked_users.items()
        ]
        # Activate drums track for changed user.
        self.activate_track(changed_user_id, Track.DRUMS)
        
    def user_added(self, user_id):
        print "User added:", user_id
        
    def user_removed(self, user_id):
        print "User removed:", user_id
        self.activate_track(user_id, None)
        user = self.kinect.user_listener.tracked_users[user_id]
        if user.role in self.user_tracks:
            for track in self.user_tracks[user.role].values():
                track.get_recording_track().stop()

    def recording_ended(self, role):
        print "Activating next track for role: %s" % role
        # Activate next track
        active_track = self.active_tracks[role]
        user_id = self.get_user_id_by_role(role)
        self.activate_track(user_id, (active_track + 1) % 3)
        
    def get_user_id_by_role(self, role):
        for user_id, user in self.kinect.user_listener.tracked_users.items():
            if user.role == role:
                return user_id
                
    def get_track_named(self, name):
    	""" Returns the Track with the specified name, or None if not found. """
    	for track in self.live_set.tracks:
    		if track.name == name:
    			return track
    	raise KeyError(name)
        
    def stop(self):
        print "Stopping Ableton thread"
        self.ableton_thread_stop_event.set()
        print "Waiting for Ableton thread to finish"
        exited_gracefully = self.ableton_thread_exited_event.wait(5)
        if not exited_gracefully:
            print "Ableton thread not stopped after 5 seconds, exiting anyway."
        print "Stopping Kinect"
        self.kinect.stop()

def main():
    looper = KinectLooper()
    looper.start()
    graphics.start(looper)
    # This code will only run if the user quits the app (by pressing Esc or closing the window),
    # or if the Ableton thread crashes and exits the pyglet app.
    looper.stop()
    
class Track(object):
    DRUMS = 0
    HARMONY = 1
    MELODY = 2



    
if __name__ == "__main__":
    main()
