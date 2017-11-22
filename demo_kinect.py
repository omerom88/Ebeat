from random import randint
class KinectDemoInterface(object):
    def __init__(self):
        pass

    def start(self):
        while True:
            continue

    def get_joint_positions(self):
        return [(i * randint(0,50), i * randint(0,50)) for i in range(15)]
        #return [(i * 50, i * 50) for i in range(15)]