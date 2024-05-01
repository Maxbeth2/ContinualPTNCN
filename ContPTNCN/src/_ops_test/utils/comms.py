# import serial
from pythonosc import udp_client
import time
import serial.tools.list_ports

PORT_IDENTIFIERS = ["Arduino", "CH340", "USB2.0-Serial", "USB Serial", "Teensyduino"]

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


class ArduConn():
    """
    Reads and writes serial messages in the format "address:value" from Arduino

    Dependecies:
    - pyserial (install with `pip install pyserial`)
    """
    def __init__(self, channel_filters):
        self.channel_filters = channel_filters
        print("Trying to establish a connection to Arduino...")
        # List all devices connected to this computers Serial Ports
        list_comport_devices()

        # Find the first devices that seems to be an Arduino
        arduino_port = find_first_arduino_port()
        self.arduino = serial.Serial(port=arduino_port, baudrate=115200, timeout=.1)
        self.arduino.flushInput()
        print(f"Established a serial connection to device at {arduino_port}")


    def read_to_string(self):
        try:
            serialdata = self.arduino.readline()
            received_string = serialdata.decode("utf-8").strip()
            address, value = received_string.split(":")
            print("val: ")
            print(value)
            if address not in self.channel_filters:
                return ""
            return received_string
        except:
            # print("ERRRRRRR")
            return ""
    
    def write(self, val):
        self.arduino.write(val)
        

class SCWriter:
    """Writes to a port
    - deps: python-osc (install with `pip install python-osc`)"""
    def __init__(self, OSC_IP="127.0.0.1", OSC_PORT=7771):
        # A list of strings which identify a valid "Arduino" for us.
        # Use something from the description of list_comport_devices()
        self.OSC_IP = OSC_IP
        self.OSC_PORT = OSC_PORT
        print(f"Creating OSC client which will send OSC data to {OSC_IP}:{OSC_PORT}")
        self.client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)
        print("\nListening for incoming messages:")
    
    def write_from_string(self, received_string):
        if received_string != "" and ":" in received_string:
            address, value = received_string.split(":")
            print(value)
            # value = float(value) * 50.0
            self.client.send_message(address, value)
                
        

