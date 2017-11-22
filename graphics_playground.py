import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
from kinect import KinectInterface
from threading import Thread
import graphic

kinect = KinectInterface()

def start_kinect_tracking():
    kinect.start()

def start_graphics_thread():
    t = Thread(target=graphics_thread)
    t.start()

def graphics_thread():
    graphic.start(kinect)

def main():
    start_graphics_thread()
    start_kinect_tracking()


if __name__ == "__main__":
    main()
