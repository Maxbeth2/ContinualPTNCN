import multiprocessing as mp
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

class StreamFromSCProcess(mp.Process):
    def __init__(self, feed_pipe):
        mp.Process.__init__(self)
        self.feed_pipe = feed_pipe
        self.server = BlockingOSCUDPServer("localhost", 7001, dispatcher=Dispatcher())

    def run(self):
        pass