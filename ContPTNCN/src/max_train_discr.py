from models.max_net import PTNCN_MAX

from processes.arduinout_process import ArduInOutProcess
from processes.sc_recieive_process import SCReceiveProcess
from processes.vis_ui_process import UIProcess
from pynput import keyboard

def get_ardu():
    import serial
    import serial.tools
    import serial.tools.list_ports
    port = None
    for p in serial.tools.list_ports.comports():
        in_description = any(x in p.description for x in ["Arduino"])
        if in_description:
            port = p
    arduino = serial.Serial(port=port.device, baudrate=38400, timeout=.1)
    return arduino

ardu = get_ardu()

from multiprocessing.connection import Pipe
beat_feed, beat_recv = Pipe()
switch_trigger, trigger_switch = Pipe()
plot_feed, plot_recv = Pipe()
command_feed, command_recv = Pipe()

global save_command
global reset_command
save_command = False
reset_command = False
# 
def on_press(key):
    try:
        if key.char == 'b':
            command = f"3:{"b"}"
            ardu.write(command.encode())
        
    except AttributeError:
        pass

def on_release(key):
    global save_command
    global reset_command
    try:
        if key.char == 's':
            save_command = True
        if key.char == 'r':
            reset_command = True
    except:
        pass


listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()





def empty_buffers():
    while beat_recv.poll():
        beat_recv.recv()
    while trigger_switch.poll():
        trigger_switch.recv()     



model = PTNCN_MAX([20, 20, 9])

import random as r
import time as t
if __name__ == '__main__':
    scr_proc = SCReceiveProcess(beat_feed, switch_trigger, feed_plot_pipe=plot_feed)
    scr_proc.start()
    ard_proc = ArduInOutProcess()
    ard_proc.start()
    ui_proc = UIProcess(plot_recv, command_pipe=command_recv)
    ui_proc.start()


    
    Aseq = [r.randint(0,20) for i in range(8)]
    Bseq = [r.randint(0,20) for i in range(8)]

    i = 0
    x = 0
    while True:
        # wait for downbeat
        while not beat_recv.poll():
            pass
        empty_buffers()

        # wait for upbeat
        while not trigger_switch.poll():
            pass
        
        command = f"1:{Aseq[x]}&2:{Bseq[x]}"
        # plot_feed.send({"A": Aseq[x], "B":Bseq[x]})
        ardu.write(command.encode())
        i += 1
        x = i % len(Bseq)

        empty_buffers()

        if save_command:
            print("saving")
            save_command = False
            command_feed.send("save")
        
        if reset_command:
            print("resetting")
            reset_command = False
            command_feed.send("reset_rec")
        

    