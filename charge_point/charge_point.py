import asyncio
import websockets
from datetime import datetime
from random import randrange

# from ocpp.v16 import call, ChargePoint as cp
# # # from ocpp.v16.enums import RegistrationStatus, AvailabilityStatus, AvailabilityType
# from ocpp.v16.enums import *
# ##for serial connections
# import serial
from evse_functions import *
from ocpp_chargepoint_class import ChargePoint

ENCODER = True
CHARGE_POINT_MODEL = "openEVSE-D2V"
CHARGE_POINT_VENDOR = "Pura Cepa"
HEARTBEAT_INTERVAL = 1
RFID_VALUE = "1234"
CONNECTOR_ID = 1
AUTHORIZED = False
TRANSACTION_ID = 1
TRANSACTION_STATUS = False
METER_VALUES = 0

class VehicleCharge:
  def __init__(self, rfid, connector_id, authorize,
             transaction_id, transaction_status, meter_values):
    self.rfid = rfid
    self.connector_id = connector_id
    self.authorize = authorize
    self.transaction_id = transaction_id
    self.transaction_status = transaction_status
    self.meter_values = meter_values

####################################################################################################
# FIRST CORE FUNCTION
async def boot_heartbeat(cp, c_p_model, c_p_vendor):
    #BOOT NOTIFICATION
        # Ejecutar Boot notification solo la primera vez que se conecta un OpenEVSE:
        # ---> Charge point model (seted at start)
        # ---> Charge point vendor (seted at start)
        # Respuesta: verificar si "status" = ACCEPTED
        # Guardar "interval" para usar en heart beat

    #HEART BEAT
        # Ejecutar heart beat sin datos.
        # La respuesta del tiempo se puede usar para sincronizar con reloj interno
    global HEARTBEAT_INTERVAL
    HEARTBEAT_INTERVAL = await cp.send_boot_notification(c_p_model, c_p_vendor)
    await cp.send_heartbeat(HEARTBEAT_INTERVAL)

####################################################################################################
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

async def full_charge(cp, ser, v_charge):
    global HEARTBEAT_INTERVAL
    await asyncio.sleep(15)
    while True:
        v_charge.rfid = str(input("ingrese RFID tag:"))
        v_charge.authorize = await cp.send_authorize(v_charge.rfid)
        if v_charge.authorize:
            # print("entro al authorized")
            timest = datetime.utcnow().isoformat()
            # status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
            global_energy = 5
            # print("obtuvo datos")
            v_charge.transaction_id, v_charge.transaction_status = await cp.send_start_transaction(v_charge, global_energy, timest)
            # print("mando transaccion")
            if v_charge.transaction_status:
                # ENABLE CHARGE
                print("enable open EVSE")
                # enable_open_EVSE = set_enable(ser,encode=ENCODER)
                # SET VALUES
                # set_display_color(ser, color_int=5, encode=ENCODER)
            a=0
            while True:
                a+=1
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                # status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                # await cp.send_meter_values(connector_id, [[[timest], [session_energy]]])
                print("meter_values: ", a)
                if a==4:
                    break
            v_charge.authorize = await cp.send_authorize(v_charge.rfid)
            if v_charge.authorize:
                timest = datetime.utcnow().isoformat()
                # status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                global_energy = 10
                print("disable open EVSE")
                # disable_open_EVSE = set_disable(ser, encode=ENCODER)
                v_charge.transaction_status = await cp.send_stop_transaction(global_energy, timest, v_charge.transaction_id)
        else:
            print("The RFID number: ", v_charge.rfid, "was not authorized by central system")

async def main():
    #Connection usb-serial with openEVSE and disable
    # ser = start_connection(SERIAL_NAME, BAUDRATE, TIMEOUT)
    ser = 1
    # disable_open_EVSE = set_disable(ser,encode=True)

    async with websockets.connect(
        'ws://localhost:9000/CP_1',
         subprotocols=['ocpp1.6']
    ) as ws:

        #Init chargePoint
        cp = ChargePoint('CP_1', ws)
        
        #Boot nofitication step
        c_p_model = CHARGE_POINT_MODEL
        c_p_vendor = CHARGE_POINT_VENDOR

        #Charging values
        vc = VehicleCharge(
            RFID_VALUE,
            CONNECTOR_ID,
            AUTHORIZED,
            TRANSACTION_ID,
            TRANSACTION_STATUS,
            METER_VALUES
        )

        await asyncio.gather(
                cp.start(),
                boot_heartbeat(cp, c_p_model, c_p_vendor),
                full_charge(cp, ser, vc),
                # cp.send_boot_notification(c_p_model, c_p_vendor),
                # cp.send_authorize(tag_rfid),
                # cp.send_heartbeat(),
                # evse_status(ser)
                # cp.send_change_availability(con_id, av_type),
                # cp.send_start_transaction(con_id, tag_rfid, global_energy, time_string)
                )

if __name__ == '__main__':
    asyncio.run(main())
