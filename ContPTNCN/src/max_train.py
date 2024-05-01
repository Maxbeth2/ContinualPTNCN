from models.max_net import PTNCN_MAX

# from utils.comms import ArduConn, SCWriter

from processes.arduinout_process import ArduInOutProcess
# from processes.sc_stream_process import StreamFromSCProcess
# from models.model_utils.s_a import Actuator, Sensor

from processes.plotting_process import PlottingProcess

from processes.sc_recieive_process import SCReceiveProcess

from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher



model = PTNCN_MAX([20, 20, 9])
# sens = Sensor()
# act = Actuator()

from multiprocessing.connection import Pipe
ardu_feed, ardu_get = Pipe()

SC_feed, SC_fetch = Pipe()

act_feed, act_rec = Pipe()

beat_feed, beat_recv = Pipe()
switch_trigger, trigger_switch = Pipe()
# sc_to_model = StreamFromSCProcess(SC_feed)

plot_feed, plot_recv = Pipe()


import random as r
if __name__ == '__main__':
    scr = SCReceiveProcess(beat_feed, switch_trigger)
    scr.start()
    ardu_to_sc = ArduInOutProcess(plt_feed_pipe=plot_feed, act_pipe=act_rec, trigger_switch=trigger_switch)
    ardu_to_sc.start()
    pp = PlottingProcess(plot_recv, beat_recv)
    pp.start()

    while True:
        if beat_recv.poll():
            print(beat_recv.recv())
        a = r.randint(0,10)
        b = r.randint(0,10)
        act_feed.send(f"{a},{b}")

