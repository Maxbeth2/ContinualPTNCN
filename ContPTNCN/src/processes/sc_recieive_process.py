import multiprocessing as mp
import multiprocessing.connection as mpc
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

from pynput import keyboard

import numpy as np

class SCReceiveProcess(mp.Process):
    def __init__(self, feed_beat_pipe : mpc.Connection, 
                 feed_switch_pipe : mpc.Connection,
                 feed_plot_pipe : mpc.Connection,
                #  recv_command_pipe : mpc.Connection
                 ):
        mp.Process.__init__(self)
        self.feed_beat_pipe = feed_beat_pipe
        self.feed_switch_pipe = feed_switch_pipe
        self.feed_plot_pipe = feed_plot_pipe
        # self.recv_command_pipe = recv_command_pipe


    def run(self):
        global Lrec, Rrec
        Lrec = []
        Rrec = []

        def action_handler(unused_addr, args, a):
            self.feed_switch_pipe.send(args[0])
            # print("action", args[0])
        def beat_handler(unused_addr, args, b):
            self.feed_beat_pipe.send(args[0])

        def note_handler(unused_addr, args, lr_n):
            self.feed_beat_pipe.send(args[0])
            ln, rn = lr_n.split(":")
            ln = int(ln.strip())
            rn = int(rn.strip())
            Lrec.append(ln)
            Rrec.append(rn)
            self.feed_plot_pipe.send({"A": ln, "B": rn})
            
            # print("L", Lrec)
            # if args[0] == "left_note":
            #     Lrec.append(n)
            #     # print("L", rec)
            # if args[0] == "right_note":
            #     # print("R", n)

            # print("handling beat", b)

        

        dispatcher = Dispatcher()
        dispatcher.map("/a1", action_handler, "..receive_action")
        dispatcher.map("b1", beat_handler, "beat")
        dispatcher.map("/n1", note_handler, "left_note") # WHY SEND 3??
        # dispatcher.map("/r1", note_handler, "right_note")
        server = osc_server.ThreadingOSCUDPServer(server_address=("localhost", 7001), dispatcher=dispatcher)
        # server = osc_server.AsyncIOOSCUDPServer(server_address=("localhost", 7001), dispatcher=dispatcher)
        server.serve_forever()
        # print("HERE")
        # while True:
        #     if self.recv_command_pipe.poll():
        #         print("HERE")
        #         command = self.recv_command_pipe.recv()
        #         if command == "save":
        #             data = np.array([Lrec,Rrec])
        #             print("SAVING DATA")
        #             print(data)
        #             np.save("test_data", data)