import multiprocessing as mp
from multiprocessing.connection import Connection

import serial
import time
import serial.tools.list_ports
from pythonosc import udp_client



from PyQt6 import QtCore, QtWidgets
import pyqtgraph as pg
import pyqtgraph.examples as ex
# ex.run()
# import atexit

class PlottingProcess(mp.Process):
    """
    Starts a synth on a running SCServer. Looks for OSC messages containing pitch information on serial and updates the pitch of the synth accordingly.
    """
    def __init__(self, input_pipe, beat_recv_pipe : Connection):
        mp.Process.__init__(self)
        self.input_pipe = input_pipe
        self.beat_recv_pipe = beat_recv_pipe
        self.xdata = []
        self.mudata = []
        self.beat_data = []
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
        x_curve = pg.PlotCurveItem(pen='b')
        mu_curve = pg.PlotCurveItem(pen='y')
        beat_curve = pg.PlotCurveItem(pen='r')
        p0.addItem(x_curve)
        p0.addItem(mu_curve)
        p0.addItem(beat_curve)
        x_curve.setData(self.xdata)
        mu_curve.setData(self.mudata)
        beat_curve.setData(self.beat_data)
        
        self.input_pipe : Connection


        def update():
            winSz = 500
            

            if self.input_pipe.poll():
                if self.beat_recv_pipe.poll():
                    self.beat_recv_pipe.recv()
                    self.beat_data.append(5.0)
                else:
                    self.beat_data.append(1.0)
                data = self.input_pipe.recv()
                # print("DATA",data,"\n\n")
                # x = data['x']
                # mu = data['mu']
                self.xdata.append(float(data["A"]))
                self.mudata.append(float(data["B"]))
                
                # self.mudata.append(mu)
                # self.xdata.append(x)
                self.last_val = data
                while self.input_pipe.poll():
                    self.input_pipe.recv()
            # else:
            #     self.data.append(self.last_val)
            
            l = len(self.xdata)
            if l > winSz:
                x_curve.setData(self.xdata[l-winSz:-1])
                mu_curve.setData(self.mudata[l-winSz:-1])
                beat_curve.setData(self.beat_data[l-winSz:-1])
            else:
                x_curve.setData(self.xdata)
                mu_curve.setData(self.mudata)
                beat_curve.setData(self.beat_data)


        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(16)
        timer.setInterval(16)
        app.exec()

       