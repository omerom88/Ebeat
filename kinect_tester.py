from threading import Thread, Event
from kinect import KinectInterface
import time
import signal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


exit_event = Event()

def signal_handler(signal, frame):
        print "User pressed Ctrl+C!"
        exit_event.set()
signal.signal(signal.SIGINT, signal_handler)


def start_kinect_tracking():
    global kinect
    kinect = KinectInterface()
    kinect.start()
    
def start_monitor_thread():
    t = Thread(target=monitor_thread)
    t.daemon = True
    t.start()

def monitor_thread():
    while not exit_event.wait(1):
        for user_id, user in kinect.user_listener.tracked_users.iteritems():
            formatted_params = ", ".join("%.2f" % p for p in user.param_values)
            print "User %s: (%s)" % (user_id, formatted_params)

fig, ax = plt.subplots()
x = np.arange(0, 2*np.pi, 0.01)
line, = ax.plot(x, np.sin(x))
def show_graph():
    ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init, interval=500, blit=False)
    plt.show()

def animate(i):
    #line.set_ydata(np.sin(x + i/10.0))  # update the data
    if kinect.user_listener.tracked_users:
        user = kinect.user_listener.tracked_users.values()[0]
        #mean_joint_distance = user.saved_joint_distances.tail(1).mean().mean()
        mean_joint_distance = user.mean_joint_distance
        #print mean_joint_distance
        new_data = np.append(line.get_ydata()[1:], mean_joint_distance)
        print "X:", len(line.get_xdata()), "Y:", len(line.get_ydata()), "New:", len(new_data)
        line.set_ydata(new_data)
    return line,

# Init only required for blitting to give a clean slate.
def init():
    line.set_ydata(np.ma.array(x, mask=True))
    return line,


def main():
    start_kinect_tracking()
    start_monitor_thread()
    # This runs the kinect loop until Ctrl+C
    #signal.pause()
    show_graph()
    kinect.stop()

if __name__ == "__main__":
    main()
