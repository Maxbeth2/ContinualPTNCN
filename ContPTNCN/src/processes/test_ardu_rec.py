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


arduino = get_ardu()
import time
wait = False

while True:
    data = arduino.readline()
    received_string = data.decode("utf-8").strip()
    print(received_string)
    if received_string != "" and ":" in received_string:
        addr, line = received_string.split(":")
        ch1, ch2 = line.split(",")
        # print(f"ch1: {float(ch1)}, ch2: {float(ch2)}")
    # print("asdasd")
        value = input("enter in format 'a,b': ")
        A, B = value.split(",")
        command = f"1:{A}&2:{B}"
        arduino.write(command.encode())


