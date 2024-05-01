import multiprocessing as mp
import multiprocessing.connection as mpc
from pynput import keyboard
import serial
from pythonosc import udp_client
import time


class ArduInOutProcess(mp.Process):
    """
    Starts a synth on a running SCServer. Looks for OSC messages containing pitch information on serial and updates the pitch of the synth accordingly.
    """
    def __init__(self, 
                #  plt_feed_pipe : mpc.Connection, 
                #  act_pipe : mpc.Connection, 
                #  trigger_switch: mpc.Connection,
                 OSC_PORT=57120):
        mp.Process.__init__(self)
        self.OSC_PORT = OSC_PORT
        # self.act_pipe = act_pipe
        # self.plt_feed_pipe = plt_feed_pipe
        # self.trigger_switch = trigger_switch


    def run(self):
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
            arduino.flush()
            for _ in range(100):
                arduino.readline()
            return arduino
        
        OSC_IP = "127.0.0.1"
        OSC_PORT = self.OSC_PORT

        arduino = get_ardu()

        print(f"Creating OSC client which will send OSC data to {OSC_IP}:{OSC_PORT}")
        client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

        print("\nListening for incoming messages:")


        while True:
            try:    
                serialdata = arduino.readline()
                received_string = serialdata.decode("utf-8").strip()
                # print(received_string)
                if received_string != "" and ":" in received_string:
                    address, value = received_string.split(":")
                    a, b = value.split(",")
                    # print(a)
                    # self.plt_feed_pipe.send({"A": a, "B": b})
                    client.send_message("/chA", a)
                    client.send_message("/chB", b)

            except KeyboardInterrupt:
                # synth.free()
                pass