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
    def __init__(self, input_pipe):
        mp.Process.__init__(self)
        self.input_pipe = input_pipe
        self.xdata = []
        self.mudata = []
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
        x_curve = pg.PlotCurveItem()
        mu_curve = pg.PlotCurveItem()
        p0.addItem(x_curve)
        p0.addItem(mu_curve)
        x_curve.setData(self.xdata)
        mu_curve.setData(self.mudata)
        
        self.input_pipe : Connection


        def update():
            winSz = 500
            if self.input_pipe.poll():
                data = self.input_pipe.recv()
                x = data['x']
                mu = data['mu']
                self.xdata.append(x)
                self.mudata.append(mu)
                self.last_val = data
                while self.input_pipe.poll():
                    self.input_pipe.recv()
            # else:
            #     self.data.append(self.last_val)
            
            l = len(self.xdata)
            if l > winSz:
                x_curve.setData(self.xdata[l-winSz:-1])
                mu_curve.setData(self.mudata[l-winSz:-1])
            else:
                x_curve.setData(self.xdata)
                mu_curve.setData(self.mudata)


        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(16)
        timer.setInterval(16)
        app.exec()

       