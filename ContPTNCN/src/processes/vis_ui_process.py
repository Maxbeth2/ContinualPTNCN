import multiprocessing as mp
from multiprocessing.connection import Connection

import serial
import time
import serial.tools.list_ports
from pythonosc import udp_client



from PyQt6 import QtCore, QtWidgets
import pyqtgraph as pg
import pyqtgraph.examples as ex

import numpy as np
# ex.run()
# import atexit

class UIProcess(mp.Process):
    def __init__(self, 
                 input_pipe : Connection,
                 command_pipe : Connection
                 ):
        mp.Process.__init__(self)
        self.input_pipe = input_pipe
        self.command_pipe = command_pipe
        # self.beat_recv_pipe = beat_recv_pipe
        self.l_data = []
        self.r_data = []
        self.beat_data = []
        self.save_l_data = []
        self.save_r_data = []
        # self.last_val = 0
        # self.last_val = 0

    def run(self):
        app = pg.mkQApp("Control Monitor")
        win = pg.GraphicsLayoutWidget(show=True)
        win.resize(1200, 600)
        win.setWindowTitle('Control Monitor')

        layout = pg.LayoutWidget()
        layout.addWidget(win)
        layout.show()
        p0 = win.addPlot()
        l_curve = pg.PlotCurveItem(pen='b')
        r_curve = pg.PlotCurveItem(pen='y')
        beat_curve = pg.PlotCurveItem(pen='r')
        p0.addItem(l_curve)
        p0.addItem(r_curve)
        p0.addItem(beat_curve)
        l_curve.setData(self.l_data)
        r_curve.setData(self.r_data)
        beat_curve.setData(self.beat_data)

        self.A = 0
        self.B = 0

        

        # def on_press(key):
        #     pass

        # def on_release(key):
        #     try:
        #         if key.char == 's':
        #             print("aa")
        #             # print(self.l_data[-1])
        #     except:
        #         pass
            # global save_command
            # try:
            #     if key.char == 's':
            #             save_command = True
            # except:
            #     pass


        # listener = keyboard.Listener(
        #     on_press=on_press,
        #     on_release=on_release)
        # listener.start()
        

        def update():
            winSz = 500
            
            if self.input_pipe.poll():
                # if self.beat_recv_pipe.poll():
                #     self.beat_recv_pipe.recv()
                #     self.beat_data.append(5.0)
                # else:
                #     self.beat_data.append(1.0)
                
                data = self.input_pipe.recv()
                self.A = float(data["A"])
                self.B = float(data["B"])
                # print("A", self.A)
                self.save_l_data.append(self.A)
                self.save_r_data.append(self.B)
            else:
                self.l_data.append(self.A)
                self.r_data.append(self.B)

                # print("DATA",data,"\n\n")
                # x = data['x']
                # mu = data['mu']
                
                
                # self.mudata.append(mu)
                # self.xdata.append(x)
                # self.last_val = data
            while self.input_pipe.poll():
                self.input_pipe.recv()
            # else:
            #     self.data.append(self.last_val)
            
            l = len(self.l_data)
            if l > winSz:
                l_curve.setData(self.l_data[l-winSz:-1])
                r_curve.setData(self.r_data[l-winSz:-1])
                # beat_curve.setData(self.beat_data[l-winSz:-1])
            else:
                l_curve.setData(self.r_data)
                r_curve.setData(self.l_data)
                # beat_curve.setData(self.beat_data)

            if self.command_pipe.poll():
                command = self.command_pipe.recv()
                if command == "save":
                    with open('max_improv_data.txt', 'a') as recording_log:
                        for i in range(len(self.save_l_data)):
                            d_point = f"{int(self.save_l_data[i])}:{int(self.save_r_data[i])}"
                            recording_log.write(d_point)
                            if i < len(self.save_l_data) -1:
                                recording_log.write(",")
                        recording_log.write("\n")
                    self.save_r_data = []
                    self.save_l_data = []
                if command == "reset_rec":
                    self.save_r_data = []
                    self.save_l_data = []


        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(16)
        timer.setInterval(16)
        app.exec()

       