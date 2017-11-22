import pandas as pd
from pandas import DataFrame, Series
import math
from primesense import openni2, nite2
import time
import numpy as np

class Person(object):
    MOVEMENT_SMOOTHING_WINDOW_SIZE_SECONDS = 0.1
    
    def __init__(self):
        # lh_y, rh_y, head_y, body_z, hand_dist
        self.param_values = [0, 0, 0, 0, 0]
        self.saved_joint_distances = DataFrame()
        self.last_joint_positions = None
        self.skeleton = None
        self.mean_joint_distance = 0
        self.role = None
        
    def update_skeleton(self, skeleton, timestamp):
        self.skeleton = nite2.Skeleton(skeleton)
        # Round to milliseconds
        timestamp = round(timestamp, 3)
        timestamp_datetime = pd.to_datetime(timestamp, unit="s")
        skeleton = nite2.Skeleton(skeleton)
        joint_positions = self.get_joint_positions()
        #print "Joint positions:", joint_positions
        # TODO: ignore low confidence joints
        if self.last_joint_positions is not None:
            joint_distances = [calcDist(p1, p2) for p1, p2 in zip(joint_positions, self.last_joint_positions)]
            #print "Joint distances:", joint_distances
            joint_distances_series = Series(joint_distances, name=timestamp_datetime)
            self.saved_joint_distances = self.saved_joint_distances.append(joint_distances_series)
            
        self.last_joint_positions = joint_positions
        window_start_epoch = time.time() - self.MOVEMENT_SMOOTHING_WINDOW_SIZE_SECONDS
        window_start = pd.to_datetime(window_start_epoch, unit="s")
        #self.saved_joint_distances.sort(inplace=True)
        self.saved_joint_distances = self.saved_joint_distances.truncate(before=window_start)
        
        # Weighted average
        #print "Saved:"
        #print self.saved_joint_distances
        resampled = self.saved_joint_distances.asfreq("1ms").fillna(0)
        self.mean_joint_distance = resampled.mean().mean()
        #self.normalized_mean_joint_distance = self.mean_joint_distance / 
        #print "Mean joint movement:", mean_joint_distance
        
        #if len(self.saved_joint_distances.shape) == 25:
        #    print "yoo"
        
        head, neck, left_shoulder, right_shoulder, left_elbow, right_elbow, left_hand, right_hand, \
        torso, left_hip, right_hip, left_knee, right_knee, left_foot, right_foot = self.get_joints()

        #################       get hands y height       #################
        min_hands = -300
        max_hands = 820
        if left_hand.positionConfidence >= 0.5:
            left_hand_pos = float(left_hand.position.y - min_hands) / (max_hands - min_hands)
            left_hand_pos = min(1, max(0, left_hand_pos))
            self.param_values[0] = left_hand_pos
            # print "~~~~~~~~~~~~~~~~~~~~ Left Hand Y cord: ", left_hand.position.y, "   ~~~~~~~~~~~~~~~~~~~~~~~"

        if right_hand.positionConfidence >= 0.5:
            right_hand_pos = float(right_hand.position.y - min_hands) / (max_hands - min_hands)
            right_hand_pos = min(1, max(0, right_hand_pos))
            self.param_values[1] = right_hand_pos
            # print "~~~~~~~~~~~~~~~~~~~~ Right Hand Y cord: ", right_hand.position.y, "   ~~~~~~~~~~~~~~~~~~~~~~~"


        #################       get head position       #################
        max_head = 450
        min_head = -140
        if head.positionConfidence >= 0.5:
            relitive_head = min(1, max(0, float(head.position.y - min_head) / float(max_head - min_head)))
            # print "~~~~~~~~~~~~~~~~~~~~ Raw head position: ", head.position.y
            # print "~~~~~~~~~~~~~~~~~~~~ Relative head position: ", relitive_head, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            self.param_values[2] = relitive_head


        #################       get body position (front-back)       #################
        if torso.positionConfidence >= 0.5:
            body_pos = torso.position.z
            min_dist = 1200
            max_dist = 2750
            relative_body_distance = float(body_pos - min_dist) / (max_dist - min_dist)
            relative_body_distance = min(1, max(0, relative_body_distance))
            self.param_values[3] = relative_body_distance
            # print "~~~~~~~~~~~~~~~~~~~~ Torso position: ", body_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            # print "~~~~~~~~~~~~~~~~~~~~ Relative torso position: ", relative_body_distance



        #################       get hands distance       #################
        if right_hand.positionConfidence >= 0.5 and left_hand.positionConfidence >= 0.5:
            hands_distance = calcDist(right_hand.position, left_hand.position)
            hands_distance_pos = min(float(hands_distance) / float(1000), 1)
            # print "~~~~~~~~~~~~~~~~~~~~ Hands Position: ", hands_distance, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            # print "~~~~~~~~~~~~~~~~~~~~ Relative hand distance: ", hands_distance_pos
            self.param_values[4] = hands_distance_pos
            
        if neck.positionConfidence >= 0.5 and torso.positionConfidence >= 0.5:
            torso_vector = get_vector(neck.position, torso.position)
            if right_hand.positionConfidence >= 0.5 and right_shoulder.positionConfidence >= 0.5:
                rh_vector = get_vector(right_hand.position, right_shoulder.position)
                rh_angle_rad = angle_between(torso_vector, rh_vector)
                self.rh_angle = rh_angle_rad / math.pi * 180
            if left_hand.positionConfidence >= 0.5 and left_shoulder.positionConfidence >= 0.5:
                lh_vector = get_vector(left_hand.position, left_shoulder.position)
                lh_angle_rad = angle_between(torso_vector, lh_vector)
                self.lh_angle = lh_angle_rad / math.pi * 180

    def get_joint_positions(self):
        return [joint.position for joint in self.get_joints()]

    def get_joints(self):
        return [self.skeleton.get_joint(i) for i in xrange(15)]



# func to calc euclidean distance
def calcDist(right_position, left_position):
    return math.sqrt(pow(abs(right_position.x - left_position.x), 2) + \
                     pow(abs(right_position.y - left_position.y), 2) + \
                     pow(abs(right_position.z - left_position.z), 2))

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def get_vector(p1, p2):
    return (p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)
