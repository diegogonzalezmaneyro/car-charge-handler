import asyncio
import websockets
from datetime import datetime
from random import randrange

# from ocpp.v16 import call, ChargePoint as cp
# # from ocpp.v16.enums import RegistrationStatus, AvailabilityStatus, AvailabilityType
# from ocpp.v16.enums import *
# ##for serial connections
# import serial
from evse_functions import *
from ocpp_chargepoint_class import ChargePoint

CONNECTOR_ID = 1
CHARGE_POINT_MODEL = "openEVSE-D2V"
CHARGE_POINT_VENDOR = "Pura Cepa"
RFID_VALUE = "1234"
HEARTBEAT_INTERVAL = 1
TRANSACTION_ID = 0

# async def evse_status(ser):
#     while True:
#         await asyncio.sleep(5)
#         status_energy, session_energy, global_energy = get_energy_usage(ser,encode=True)
#         set_display_color(ser, color_int=randrange(7), encode=True)


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
    await cp.send_boot_notification(c_p_model, c_p_vendor)
    await cp.send_heartbeat()

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
                # boot_heartbeat(cp, c_p_model, c_p_vendor),
                # full_charge(cp, tag_rfid, con_id),
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

