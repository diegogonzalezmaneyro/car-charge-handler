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
#SERIAL_NAME = '/dev/ttyUSB0'

## connection settings
BAUDRATE = 115200
TIMEOUT = 1 # secs
# PARITY = serial.PARITY_NONE,
# STOPBITS = serial.STOPBITS_ONE,
# BYTESIZE = serial.EIGHTBITS
VERBOSE = True

#############################################
################ CONNECTION #################
#############################################
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

#############################################
################ EVSE STATUS ################
#############################################

def set_enable(ser, encode=False):
    ## command string to enable EVSE
    COMMAND = "$FE\r"
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.decode().split("^")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split("^")

    status = aux[0]
    if VERBOSE:
        print('RESPONSE: ', aux)
        print("ENABLE: ", status)
    return status

def set_reset(ser, encode=False):
    ## command string to reset EVSE
    COMMAND = "$FR\r"
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.decode().split("^")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split("^")

    status = aux[0]
    if VERBOSE:
        print('RESPONSE: ', aux)
        print("RESET: ", status)

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
        # print(line)
        aux = line.decode().split("^")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split("^")

    status = aux[0]
    if VERBOSE:
        print('RESPONSE: ', aux)
        print("DISABLE: ", status)

    return status

#############################################
############## SET/GET VALUES ###############
#############################################

def set_current(ser, amps,  encode=False):
    print("entro")
    ## command string to set current amps
    COMMAND = "$SC {}\r".format(amps)
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
    
    status = aux[0]
    if VERBOSE:
        print('RESPONSE: ', aux)
        print("SET CURRENT: ", status)

    return status

def get_energy_usage(ser, encode=False):
    ## command string to get energy usage
    COMMAND = "$GU\r"
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.decode().split(" ")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split(" ")
    
    if len(aux) == 3:
        status = aux[0]
        session_energy = int(aux[1])
        global_energy = int(aux[2].split("^")[0])
    else:
        status = "ok"
        # session_energy = int(aux[1])/3600000
        session_energy = 99
        # global_energy = int(aux[2].split("^")[0])/1000
        global_energy = 99
    
    if VERBOSE:
        print('RESPONSE: ', aux)
        print("ENERGY STATUS: {} ; SESSION ENERGY: {} ; GLOBAL ENERGY: {}".format(status, session_energy, global_energy))

    return status, session_energy, global_energy

def get_charging_data(ser, encode=False):
    ## command string to get charging current and voltage
    COMMAND = "$GG\r"
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
    
    if len(aux) == 3:
        status = aux[0]
        current_AMMETER = int(aux[1])
        current_VOLTMETER = int(aux[2].split("^")[0])
    else:
        status = "ok"
        current_AMMETER = 99
        current_VOLTMETER = 99
    
    if VERBOSE:
        print('RESPONSE: ', aux)
        print("CHARGING STATUS: {} ; CURRENT AMP: {} ; GLOBAL ENERGY: {}".format(status, current_AMMETER, current_VOLTMETER))

    return status, current_AMMETER, current_VOLTMETER

def get_current_settings(ser, encode=False):
    ## command string to get current settings
    COMMAND = "$GE\r"
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.decode().split(" ")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split(" ")

    if len(aux) == 3:
        status = aux[0]
        amps = int(aux[1])
        flag = int(aux[2].split("^")[0])
    else:
        status = "ok"
        amps = 99
        flag = 99

    if VERBOSE:
        print('RESPONSE: ', aux)
        print("CURRENT STATUS: {} ; AMPS: {} ; FLAG: {}".format(status, amps, flag))

    return status, amps, flag

def get_status(ser, encode=False):
    ## command string to get current settings
    COMMAND = "$GS\r"
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.decode().split(" ")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split(" ")
        
    if len(aux) == 3:
        status = aux[0]
        state = int(aux[1])
        elapsed = int(aux[2].split("^")[0])
    else:
        status = "MAL"
        state = 888
        elapsed = 99

    if VERBOSE:
        print('RESPONSE: ', aux)
        print("STATUS: {} ; STATE: {} ; FLAG: {}".format(status, state, elapsed))

    return status, state, elapsed 

#############################################
################# DISPLAY ###################
#############################################

def set_display_color(ser, color_int=1, encode=False):
    ## command string to get energy usage
    COMMAND = "$FB {}\r".format(color_int)
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.decode().split("^")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split("^")

    status = aux[0]
    if VERBOSE:
        print(aux)
        print("DISPLAY COLOR: ", status)
    
    return status

def set_display_text(ser, row, text, encode=False):
    ## command string to get energy usage
    COMMAND = "$FP 0 {} {}\r".format(row, text)
    ## write command on serial
    ## if mac --> encode=True
    if encode:
        ser.write(COMMAND.encode())
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.decode().split("^")
    else:
        ser.write(COMMAND)
        ## read info
        line = ser.readline()
        # print(line)
        aux = line.split("^")

    status = aux[0]
    if VERBOSE:
        print(aux)
        print("DISPLAY TEXT: ", status)
    
    return status

#############################################
################# FUNCTIONS #################
#############################################

def disable_by_current(current_seted, current_measure):
    mA_current = current_seted*1000
    if (current_measure-mA_current)>0:
        return True
    else:
        return False
