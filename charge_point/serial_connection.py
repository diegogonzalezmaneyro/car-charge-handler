##Librerias
import serial

## Variables
## connection from mac:
## port list using serial tools
## python -m serial.tools.list_ports
SERIAL_NAME = '/dev/cu.usbserial-A50285BI'

## connection from RPi
# SERIAL_NAME = '/dev/ttyUSB0'

## connection settings
BAUDRATE = 115200
TIMEOUT = 1 # secs
# PARITY = serial.PARITY_NONE,
# STOPBITS = serial.STOPBITS_ONE,
# BYTESIZE = serial.EIGHTBITS


def get_energy_usage(encode=False):
    ## command string to get energy usage
    COMMAND = "$GU\r"
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        print(line)
        aux = line.decode().split(" ")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        print(line)
        aux = line.split(" ")
    
    print(aux)
    status = aux[0]
    print("status: ", status)
    session_energy = int(aux[1])/3600000
    print("session energy: ", session_energy)
    global_energy = int(aux[2].split("^")[0])/1000
    print("global energy: ",global_energy)

    return status, session_energy, global_energy

def set_display_color(color_int=1,encode=False):
    ## command string to get energy usage
    COMMAND = "$FB {}\r".format(color_int)
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        print(line)
        aux = line.decode().split("^")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        print(line)
        aux = line.split("^")

    print(aux)
    status = aux[0]
    print("status: ", status)
    return status
    
try:
    ## open serial connection
    ser = serial.Serial(SERIAL_NAME,
                        baudrate=BAUDRATE,
                        timeout=TIMEOUT)
    
    print(ser)
    ## get values from openEVSE
    status, session_energy, global_energy = get_energy_usage(encode=True)
    status = set_display_color(color_int=3,encode=True)
    status = set_display_color(color_int=4,encode=True)
    status = set_display_color(color_int=5,encode=True)
    status = set_display_color(color_int=6,encode=True)
    status = set_display_color(color_int=7,encode=True)

    # ## en la RPi no es necesario encodear el texto
    # ## en mac
    # COMMAND = "$FB 1\r"
    # ser.write(COMMAND.encode())
    # ## en RPi
    # # ser.write(COMMAND)
    # line = ser.readline()
    # print(line.decode())
    # ser.write("$SE 0")
    # print("flag1")
    # line = ser.readline()
    # print("flag2")
    # print(line)
    # ser.write("$FB 1\r")
    # line = ser.readline()
    # print(line)
    # ser.write("$FB 4\r")
    # line = ser.readline()
    # print(line)
    # ser.write("$FP 0 0 BAILA_DIRA\r")
    # line = ser.readline()
    # print(line)
    # ser.write("$FB 3\r")
    # line = ser.readline()
    # print(line)
    # ser.write("$FB 7\r")
    # line = ser.readline()
    # print(line)
    
except:
    print("Connection error, check what is going on")

## some aux commands:

#ser.close 
