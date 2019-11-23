from datetime import datetime
from random import randrange

##for serial connections
import serial

######################################
######### OPENEVSE MODULE ############
######################################

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

def get_energy_usage(ser, encode=False):
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
    # global_energy = int(aux[2].split("^")[0])/1000
    global_energy = int(aux[2].split("^")[0])
    print("global energy: ",global_energy)

    return status, session_energy, global_energy

def set_display_color(ser, color_int=1, encode=False):
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

def set_enable(ser, encode=False):
    ## command string to enable EVSE
    COMMAND = "$FE\r"
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
    
def set_disable(ser, encode=False):
    ## command string to disable EVSE
    COMMAND = "$FD\r"
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

def start_connection(serial_name, baud_r, t_out):
    try:
        ## open serial connection
        ser = serial.Serial(serial_name,
                            baudrate=baud_r,
                            timeout=t_out)
        return ser
    except:
        print("Connection error, check what is going on with the Open_EVSE")

def end_connetcion(ser):
    ser.close()
