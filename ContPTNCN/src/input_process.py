import multiprocessing as mp
import multiprocessing.connection as mpc

import serial
import time
import serial.tools.list_ports
from pythonosc import udp_client

from supercollider import Server, Synth

import pyqtgraph as pg

import numpy as np

from pynput import keyboard
# ex.run()
# import atexit

class InputProcess(mp.Process):
    """
    Starts a synth on a running SCServer. Looks for OSC messages containing pitch information on serial and updates the pitch of the synth accordingly.
    """
    def __init__(self, synth_name="sinel", out_pipe=None):
        mp.Process.__init__(self)
        self.synth_name = synth_name
        self.out_pipe = out_pipe

    def run(self):
        global start_rec
        global save_rec
        recording = []
        start_rec = False
        save_rec = False
        server = Server()
        synth = Synth(server, "sines", { "freq" : 440.0, "gain" : -3.0 })
        # synth2 = Synth(server, "sinet", { "freq" : 440.0, "gain" : -3.0 })

        def on_press(key):
            global save_rec
            global start_rec
            try:
                # print(f"alphanumeric key {key.char} pressed")
                if key.char == 'r':
                    start_rec = True
                    print("rec")
                if key.char =='s':
                    save_rec = True
                    print("saved")
                    
            except AttributeError:
                print(f"special key {key} pressed")

        def on_release(key):
            # print(f"{key} relesased")
            if key == keyboard.Key.esc:
                return False
            
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        listener.start()

        """
        Receives Serial messages in the format "address:value" from Arduino
        and forward the value to the given OSC-address

        Dependecies:
        - pyserial (install with `pip install pyserial`)
        - python-osc (install with `pip install python-osc`)
        """

        # A list of strings which identify a valid "Arduino" for us.
        # Use something from the description of list_comport_devices()
        PORT_IDENTIFIERS = ["Arduino", "CH340", "USB2.0-Serial", "USB Serial", "Teensyduino"]
        # OSC IP to connect to (127.0.0.1 is the IP address of this computer)
        OSC_IP = "127.0.0.1"
        # OSC Port to connect to (7001 is default)
        OSC_PORT = 7001

        def list_comport_devices():
            """
            Print a list of devices connected to this computers serial port
            """
            # Get a full list of devices connected
            ports = [p for p in serial.tools.list_ports.comports() if p.description != "n/a"]

            if len(ports) == 0:
                # If there are no devices connected, print this
                print("Found no devices connected to this computers Serial ports\n")
            else:
                # If there are devices connected...
                print(f"Found the following devices connected to this computers serial ports:")
                # Print each of the devices out
                print(f"   n {'port':<15} {'description':<15} {'manufacturer':<15} {'product':<15}")
                print("-"*120)
                for i, p in enumerate(ports):
                    device = f"[{p.device}]"
                    print(f"  [{i}]{device:<15} {p.description:<15} {p.manufacturer if not p.manufacturer is None else 'None':<15} {p.product if not p.product is None else 'None':<15}")
                print()


        def is_suitable_device(port) -> bool:
            """
            Return true if any of the Strings in the list PORT_IDENTIFIERS is found in
            a ports description or manufacturer
            """
            in_description = any(x in port.description for x in PORT_IDENTIFIERS)
            in_manufacturer = any(x in port.manufacturer for x in PORT_IDENTIFIERS) if not port.manufacturer is None else False
            return in_description or in_manufacturer


        def find_first_arduino_port():
            """
            This function returns the first device connected to this computers
        serial port, whose description matches with any string in the list
            PORT_IDENTIFIERS. If nothing is found print a message and wait
            """
            # Get a list of devices which have any of the strings from the list
            # PORT_IDENTIFIERS in their description
            ports = [p for p in serial.tools.list_ports.comports() if is_suitable_device(p)]

            # When there are no devices found, just try again every second until
            # a device is found or the program is stopped
            while len(ports) == 0:
                try:
                    print("  No serial port with Arduino found, not connected? Stop program with [Ctrl] + [c]", end='\r', flush=True)
                    ports = [p for p in serial.tools.list_ports.comports() if is_suitable_device(p)]
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
            else:
                print("", end='\r', flush=True)

            # If a device is found, print a message and return the first one
            port = ports[0]
            print(f"  Found a suitable device connected at {port.device}: {port.description}")

            return port.device


        # -----------------------------------------------------------------------

        print("="*120)
        print(f"{'serial_to_osc.py':^120}")
        print("="*120)
        print()


        print("Trying to establish a connection to Arduino...")

        # List all devices connected to this computers Serial Ports
        list_comport_devices()

        # Find the first devices that seems to be an Arduino
        arduino_port = find_first_arduino_port()
        arduino = serial.Serial(port=arduino_port, baudrate=115200, timeout=.1)
        arduino.flushInput()
        print(f"Established a serial connection to device at {arduino_port}")

        print(f"Creating OSC client which will send OSC data to {OSC_IP}:{OSC_PORT}")
        client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

        print("\nListening for incoming messages:")

        self.out_pipe : mpc.Connection

        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


        while True:
            if save_rec:
                print("saving")
                start_rec = False
                to_save = np.array(recording)
                np.save(file='recording', arr=to_save)
                recording = []
                save_rec = False
            try:
                serialdata = arduino.readline()
                received_string = serialdata.decode("utf-8").strip()
                # print(received_string)
                if received_string != "" and ":" in received_string:
                    address, value = received_string.split(":")
                    client.send_message(address, value)
                    value = float(value)
                    if address == '/ch/1':
                        synth.set("freq", value*1.0)
                    # if address == '/ch/2':
                    #     synth2.set("freq", value*1.0)
                    # print(f"  {arduino_port} ⟶ {value} ⟶ {OSC_IP}:{OSC_PORT}{address}")
                    if start_rec and address == '/ch/1':
                        recording.append(value)
                    self.out_pipe.send(value)
                elif received_string != "" and not ":" in received_string:
                    address = "/ch/1"
                    value = float(received_string)
                    # print(f"  {arduino_port} ⟶ {value} ⟶ {OSC_IP}:{OSC_PORT}{address}")
                    client.send_message(address, value)
                    if address == '/ch/1':
                        synth.set("freq", value*1.0)
                    # if address == '/ch/2':
                    #     synth2.set("freq", value*1.0)
                    if start_rec and address == '/ch/1':
                        recording.append(value)
                    self.out_pipe.send(value)

            except KeyboardInterrupt:
                synth.free()
                