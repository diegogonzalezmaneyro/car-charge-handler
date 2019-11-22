import asyncio
import websockets

from ocpp.v16 import call, ChargePoint as cp
# from ocpp.v16.enums import RegistrationStatus, AvailabilityStatus, AvailabilityType
from ocpp.v16.enums import *
##for serial connections
import serial


CONNECTOR_ID = 1
CHARGE_POINT_MODEL = "openEVSE-D2V"
CHARGE_POINT_VENDOR = "Pura Cepa"
RFID_VALUE = "1234"

######################################
######## SERIAL CONNECTION ###########
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
    
def start_connection(serial_name, baud_r, t_out):
    try:
        ## open serial connection
        ser = serial.Serial(serial_name,
                            baudrate=baud_r,
                            timeout=t_out)
        return ser
    except:
        print("Connection error, check what is going on")

def end_connetcion(ser):
    ser.close()


class ChargePoint(cp):
    async def send_boot_notification(self, c_p_model, c_p_vendor):
        request = call.BootNotificationPayload(
            charge_point_model = c_p_model,
            charge_point_vendor = c_p_vendor
        )

        response = await self.call(request)

        global HEARTBEAT_INTERVAL
        if response.status ==  RegistrationStatus.accepted:
            print("Connected to central system.")
            HEARTBEAT_INTERVAL = response.interval

        
    async def send_authorize(self, id_tag_rfid):
        request = call.AuthorizePayload(
            id_tag = id_tag_rfid
        )

        response = await self.call(request)

        if response.id_tag_info['status'] ==  RegistrationStatus.accepted:
            print("Authorizated by central system.")
        else:
            print("For some reason we are out, go home kid")

    # async def send_change_availability(self, con_id, av_type):
    #     request = call.ChangeAvailabilityPayload(
    #         connector_id = con_id,
    #         type = av_type
    #     )

    #     response = await self.call(request)

    #     if response.status ==  AvailabilityStatus.accepted:
    #         print("Change avilability correct.")

    async def send_start_transaction(self, connector, id_tag_rfid, meter, timest):
        request = call.StartTransactionPayload(
            connector_id = connector,
            id_tag = id_tag_rfid,
            meter_start = meter,
            timestamp = timest
            # reservation_id = res_id
        )

        response = await self.call(request)
        if response:
            print("tamo en vivo")
        # if response.status ==  RegistrationStatus.accepted:
        #     print("Connected to central system.")

async def main():
    async with websockets.connect(
        'ws://localhost:9000/CP_1',
         subprotocols=['ocpp1.6']
    ) as ws:

        #Init chargePoint
        cp = ChargePoint('CP_1', ws)
        
        #Boot nofitication step
        c_p_model = CHARGE_POINT_MODEL
        c_p_vendor = CHARGE_POINT_VENDOR

        #Authorize
        tag_rfid = str(RFID_VALUE)

        #change avilability
        con_id = CONNECTOR_ID
        # av_type = AvailabilityType.operative

        ser = start_connection(SERIAL_NAME, BAUDRATE, TIMEOUT)
        status_energy, session_energy, global_energy = get_energy_usage(ser,encode=True)
        end_connetcion(ser)
        time_string = "es hoy eh"
        # res_id = 1
        await asyncio.gather(cp.start(), cp.send_boot_notification(c_p_model, c_p_vendor),
                cp.send_authorize(tag_rfid),
                # cp.send_change_availability(con_id, av_type),
                cp.send_start_transaction(con_id, tag_rfid, global_energy, time_string)
                )

if __name__ == '__main__':
    asyncio.run(main())

# INICIO PRIMIER PRUEBA CORE
    #BOOT NOTIFICATION
        # Ejecutar Boot notification solo la primera vez que se conecta un OpenEVSE:
        # ---> Charge point model (lo podemos sacar del OpenEVSE?)
        # ---> Charge point vendor (lo podemos sacar del OpenEVSE?)
        # Respuesta: verificar si "status" = ACCEPTED
        # Guardar "interval" para usar en heart beat

    #HEART BEAT
        # Ejecutar heart beat sin datos.
        # La respuesta del tiempo se puede usar para sincronizar con reloj interno
# FIN PRIMIER PRUEBA CORE

# INICIO SEGUNDA PRUEBA CORE
    #AUTHORIZE
        # Ejecutar authorize cuando aparece un ID de usuario:
        # ---> ID tag (obtenido del modulo RFID, para pruebas se puede setear uno)
        # Respuesta: verificar si IDTAG_info = ACCEPTED

    #START TRANSACTION
        # Ejecutar start transaction si IDTAG = accepted:
        # ---> ConnectorID = setear en 1 dado que solo usamos un OpenEVSE
        # ---> IDTAG ya obtenido
        # ---> meter start (OpenEVSE global_energy de funcion get_energy_usage)
        # ---> timestamp (python lib time)
        # Respuesta: IDTAG_info = ACCEPTED (deberia mantenerse igual)
        # Guardar transaction_id para usar en BKC

    #METER VALUES
        # Ejecutar meter values cada un heart beat interval:
        # ---> ConnectorID = setear en 1 dado que solo usamos un OpenEVSE
        # ---> Meter value (OpenEVSE session_energy de funcion get_energy_usage)
        # Respuesta: vuelve vacio, corroborar que vuelve algo
    #STOP TRANSACTION
        # Ejecutar al terminar una transaccion (definir en que momento se ejecuta esto)
        # ---> meter stop (OpenEVSE global_energy de funcion get_energy_usage)
        # ---> timestamp (python lib time)
        # ---> transaction_ID (obtenido de start transaction)
        # Respuesta: vuelve vacio, corroborar que vuelve algo

