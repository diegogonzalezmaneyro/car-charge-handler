import asyncio
import websockets
from datetime import datetime
from random import randrange

from ocpp.v16 import call, ChargePoint as cp
# from ocpp.v16.enums import RegistrationStatus, AvailabilityStatus, AvailabilityType
from ocpp.v16.enums import *
##for serial connections
import serial


CONNECTOR_ID = 1
CHARGE_POINT_MODEL = "openEVSE-D2V"
CHARGE_POINT_VENDOR = "Pura Cepa"
RFID_VALUE = "1234"
HEARTBEAT_INTERVAL = 1
TRANSACTION_ID = 0

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

async def evse_status(ser):
    while True:
        await asyncio.sleep(5)
        status_energy, session_energy, global_energy = get_energy_usage(ser,encode=True)
        set_display_color(ser, color_int=randrange(7), encode=True)

class ChargePoint(cp):

    ################## BOOT NOTIFICATION ##########################
    async def send_boot_notification(self, c_p_model, c_p_vendor):
        global HEARTBEAT_INTERVAL
        await asyncio.sleep(5)

        request = call.BootNotificationPayload(
            charge_point_model = c_p_model,
            charge_point_vendor = c_p_vendor
        )
        response = await self.call(request)

        if response.status ==  RegistrationStatus.accepted:
            print("Connected to central system.")
            HEARTBEAT_INTERVAL = response.interval
            print("Heartbeat changed to ", HEARTBEAT_INTERVAL," seconds")
        else:
            print("Not connected to central system")

    ################## HEARTBEAT ##########################
    async def send_heartbeat(self):
        global HEARTBEAT_INTERVAL
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)

            request = call.HeartbeatPayload()

            response = await self.call(request)

            if response.current_time:
                print("Heartbeat delivered: ", response.current_time)
            else:
                print("Heartbeat not delivered")
        
    ################## AUTHORIZE ##########################
    async def send_authorize(self, id_tag_rfid):
        await asyncio.sleep(5)
        
        request = call.AuthorizePayload(
            id_tag = id_tag_rfid
        )

        response = await self.call(request)

        if response.id_tag_info['status'] ==  RegistrationStatus.accepted:
            print("Authorizated by central system.")
            return True
        else:
            print("For some reason we are out, go home kid")
            return False

    ################## START TRANSACTION ##########################
    async def send_start_transaction(self, connector, id_tag_rfid, meter, timest):
        global TRANSACTION_ID

        request = call.StartTransactionPayload(
            connector_id = connector,
            id_tag = id_tag_rfid,
            meter_start = meter,
            timestamp = timest
            # reservation_id = res_id ### Optional
        )

        response = await self.call(request)
        if response.id_tag_info['status'] ==  AuthorizationStatus.accepted:
            response.print("Start transaction ACCEPTED")
            TRANSACTION_ID = response.transaction_id
            return True
        else:
            print("Transaction failed")
            return False

    ################## METER VALUES ##########################
    async def send_meter_values(self, connector, meter_values_list):

        request = call.MeterValuesPayload(
            connector_id = connector,
            meter_value = meter_values_list
            # transaction_id = int ### Optional
        )

        response = await self.call(request)

        if response:
            print("Meter values sent")
        else:
            print("Error in central system with meter values")

    ################## STOP TRANSACTION ##########################
    async def send_stop_transaction(self, meter_value_stop, trans_id, timest):

        request = call.StopTransactionPayload(
            meter_stop = meter_value_stop,
            timestamp = timest,
            transaction_id = trans_id
            # reason: str = None ### Optional
            # id_tag: str = None ### Optional
            # transaction_data: List = None ### Optional
        )

        response = await self.call(request)

        if response:
            print("Stop transaction ",trans_id, ", time: ", timest)
        else:
            print("Error Stopping transaction")

        
    
    # async def send_change_availability(self, con_id, av_type):
    #     request = call.ChangeAvailabilityPayload(
    #         connector_id = con_id,
    #         type = av_type
    #     )

    #     response = await self.call(request)

    #     if response.status ==  AvailabilityStatus.accepted:
    #         print("Change avilability correct.")

# FIRST CORE FUNCTION
async def boot_heartbeat(cp, c_p_model, c_p_vendor):
    #BOOT NOTIFICATION
        # Ejecutar Boot notification solo la primera vez que se conecta un OpenEVSE:
        # ---> Charge point model (lo podemos sacar del OpenEVSE?)
        # ---> Charge point vendor (lo podemos sacar del OpenEVSE?)
        # Respuesta: verificar si "status" = ACCEPTED
        # Guardar "interval" para usar en heart beat

    #HEART BEAT
        # Ejecutar heart beat sin datos.
        # La respuesta del tiempo se puede usar para sincronizar con reloj interno
    await cp.send_boot_notification(c_p_model, c_p_vendor)
    await cp.send_heartbeat()

#SECOND CORE FUNCTION
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

async def full_charge(cp, id_tag, connector_id):
    await asyncio.sleep(10)
    
    # await cp.send_authorize(id_tag)
    # if authorized:
    #     timest = datetime.utcnow().isoformat()
    #     status_energy, session_energy, global_energy = get_energy_usage(ser,encode=True)
    #     await cp.send_start_transaction(connector_id, id_tag, global_energy,timest)
    #     if trans_started:
    #         # habilitar carga
    #         set_display_color(ser, color_int=randrange(7), encode=True)




async def main():
    #Connection usb-serial with openEVSE and disable
    ser = start_connection(SERIAL_NAME, BAUDRATE, TIMEOUT)
    disable_open_EVSE = set_disable(ser,encode=True)

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

        # ser = start_connection(SERIAL_NAME, BAUDRATE, TIMEOUT)
        # status_energy, session_energy, global_energy = get_energy_usage(ser,encode=True)
        # end_connetcion(ser)
        global_energy = 5
        # time_string = datetime.utcnow().isoformat()
        # res_id = 1
        await asyncio.gather(
                cp.start(),
                boot_heartbeat(cp, c_p_model, c_p_vendor),
                full_charge(cp, tag_rfid, con_id),
                # cp.send_boot_notification(c_p_model, c_p_vendor),
                cp.send_authorize(tag_rfid),
                # cp.send_heartbeat(),
                # evse_status(ser)
                # cp.send_change_availability(con_id, av_type),
                # cp.send_start_transaction(con_id, tag_rfid, global_energy, time_string)
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

