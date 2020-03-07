import asyncio
import websockets
from datetime import datetime
import time
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
CHARGING = False
WAIT_RFID = False
# WAITING_TIME = 5 #secs

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
async def boot_heartbeat(cp, ser, c_p_model, c_p_vendor):
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
    global CHARGING

    HEARTBEAT_INTERVAL = await cp.send_boot_notification(c_p_model, c_p_vendor)
    # display_color = set_display_color(ser, 2, encode=True)
    # display_text = set_display_text(ser, 0, "__CONECTADO A___", encode=True)
    # display_text = set_display_text(ser, 1, "SISTEMA CENTRAL_", encode=True)
    
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)

        # await cp.send_heartbeat(HEARTBEAT_INTERVAL)
        await cp.send_heartbeat()
        #if CHARGING:
        #    remote_trans = await cp.send_remote_stop_transaction()
        #    if remote_trans != 0:
        #        print("IF remote_trans == vc.transaction_id --> STOP TRANSACTION")
        #else:
        #    remote_id_tag = await cp.send_remote_start_transaction()
        #    if remote_id_tag != 0:
        #        print("IF remote_id_tag == vc.rfid --> START TRANSACTION")
        #    else:
        #        print("NO START TRANSACTION RECEIVED")

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

async def full_charge(cp, ser, ws,  v_charge):
    global HEARTBEAT_INTERVAL
    global CHARGING
    global WAIT_RFID
    # global START_REMOTE
    await asyncio.sleep(10)
    while True:
        #await asyncio.sleep(HEARTBEAT_INTERVAL)
        await asyncio.sleep(5)
        display_color = set_display_color(ser, 2, encode=True)
        display_text = set_display_text(ser, 0, "___DISPONIBLE___", encode=True)
        display_text = set_display_text(ser, 1, "APROXIME TARJETA", encode=True)
        send_authorize, rfid_readed = check_rfid_input()
 
        if send_authorize:
            v_charge.rfid = rfid_readed
            v_charge.authorize = await cp.send_authorize(v_charge.rfid)
            if v_charge.authorize:
                # Display message to user
                display_text = set_display_text(ser, 0, "__TARJETA RFID__", encode=True)
                display_text = set_display_text(ser, 1, "___AUTORIZADA___", encode=True)
                await asyncio.sleep(5)

                timest = datetime.utcnow().isoformat()
                status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                status, seted_amps, flag = get_current_settings(ser, encode=True)
                # global_energy = 5
                # print("obtuvo datos")
                v_charge.transaction_id, v_charge.transaction_status = await cp.send_start_transaction(v_charge, global_energy, timest)
                # print("mando transaccion")
                if v_charge.transaction_status:
                    # ENABLE CHARGE
                    print("enable open EVSE")
                    enable_open_EVSE = set_enable(ser,encode=ENCODER)
                    _, state, _ = get_status(ser, encode=ENCODER)
                    await asyncio.sleep(5)
                    if state != 3:
                        display_color = set_display_color(ser, 3, encode=True) # color amarillo
                        display_text = set_display_text(ser, 0, "____CONECTAR____", encode=True)
                        display_text = set_display_text(ser, 1, "____VEHICULO____", encode=True)
                        conectado = False
                        while not conectado:
                            await asyncio.sleep(3)
                            try:
                                _, state, _ = get_status(ser, encode=ENCODER)
                                if state == 3:
                                    conectado = True
                            except:
                                pass

                    CHARGING = True
                    # SET VALUES
                    set_display_color(ser, color_int=6, encode=ENCODER)

                a=0
                while CHARGING:
                    # await asyncio.sleep(HEARTBEAT_INTERVAL)
                    await asyncio.sleep(5)
                    _, state, _ = get_status(ser, encode=ENCODER)
                    if state == 3:
                        CHARGING = True
                        status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                        status, current_amps, current_volts = get_charging_data(ser, encode=True)
                        current_disable = disable_by_current(seted_amps,current_amps)
                        if current_disable:
                            disable_open_EVSE = set_disable(ser, encode=True)
                            CHARGING = False
                            display_color = set_display_color(ser, 1, encode=True) # color rojo
                            display_text = set_display_text(ser, 0, "EXCESO CORRIENTE", encode=True)
                            display_text = set_display_text(ser, 1, "________________", encode=True)
                            await asyncio.sleep(10)
                            break
                        # await cp.send_meter_values(v_charge.connector_id, timest, str(a))
                        print("meter_values: ", a)
                    elif state in [1,4,6]:
                        disable_open_EVSE = set_disable(ser, encode=True)
                        CHARGING = False
                        display_color = set_display_color(ser, 1, encode=True) # color rojo
                        if state == 1:
                            display_text = set_display_text(ser, 0, "____VEHICULO____", encode=True)
                            display_text = set_display_text(ser, 1, "__DESCONECTADO__", encode=True)
                        if state == 4:
                            display_text = set_display_text(ser, 0, "___VENTILACION__", encode=True)
                            display_text = set_display_text(ser, 1, "____REQUERIDA___", encode=True)
                        if state == 6:
                            display_text = set_display_text(ser, 0, "_____FUGA A_____", encode=True)
                            display_text = set_display_text(ser, 1, "_____TIERRA_____", encode=True)                           
                        await asyncio.sleep(10)
                        break
                    elif state != 888:
                        disable_open_EVSE = set_disable(ser, encode=True)
                        CHARGING = False
                        display_color = set_display_color(ser, 1, encode=True) # color rojo
                        display_text = set_display_text(ser, 0, "_PUNTO DE CARGA_", encode=True)
                        display_text = set_display_text(ser, 1, "____EN FALLA____", encode=True)
                        await asyncio.sleep(10)
                        break

                    send_authorize, rfid_readed = check_rfid_input()

                    if send_authorize:
                        if rfid_readed == v_charge.rfid:
                            
                            disable_open_EVSE = set_disable(ser, encode=True)
                            CHARGING = False
                            display_color = set_display_color(ser, 3, encode=True) # color amarillo
                            display_text = set_display_text(ser, 0, "__FIN DE CARGA__", encode=True)
                            display_text = set_display_text(ser, 1, "___EN PROCESO___", encode=True)
                            await asyncio.sleep(5)
                            break
                        else:
                            display_color = set_display_color(ser, 3, encode=True) # color amarillo
                            display_text = set_display_text(ser, 0, "__TARJETA RFID__", encode=True)
                            display_text = set_display_text(ser, 1, "____NO VALIDA___", encode=True)
                            await asyncio.sleep(5)
                            send_authorize = False

                    a+=1
                    if a==30:
                        break

                while True:
                    if send_authorize:
                        v_charge.authorize = await cp.send_authorize(v_charge.rfid)
                        if v_charge.authorize:
                            timest = datetime.utcnow().isoformat()
                            status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                            print("disable open EVSE")
                            v_charge.transaction_status = await cp.send_stop_transaction(global_energy, timest, v_charge.transaction_id)
                            if not v_charge.transaction_status:
                                display_color = set_display_color(ser, 2, encode=True) # color verde
                                display_text = set_display_text(ser, 0, "___TRANSACCION__", encode=True)
                                display_text = set_display_text(ser, 1, "_____EXITOSA____", encode=True)
                                await asyncio.sleep(5)
                                break
                        
                    else:
                        send_authorize, rfid_readed = check_rfid_input()
                        await asyncio.sleep(5)
                        

            else:
                print("The RFID number: ", v_charge.rfid, "was not authorized by central system")
                display_color = set_display_color(ser, 1, encode=True) # color rojo
                display_text = set_display_text(ser, 0, "__TARJETA RFID__", encode=True)
                display_text = set_display_text(ser, 1, "_NO AUTORIZADA__", encode=True)
        else:
            print("NOT RFID RECEIVED")
                

def check_rfid_input():
    file = open('rfid_inputs.txt', 'r')
    a = file.readlines()
    file.close()
    aux = a[-1].split(';')
    print(time.time()-float(aux[-1]))
    if (time.time()-float(aux[-1]))<5:
        return True,  aux[0]
    else:
        return False,  str(0)

async def main():
    # #Connection usb-serial with openEVSE and disable
    # ser = start_connection(SERIAL_NAME, BAUDRATE, TIMEOUT)
    # disable_open_EVSE = set_disable(ser,encode=True)
    # display_color = set_display_color(ser, 7, encode=True)
    # display_text = set_display_text(ser, 0, "INICIANDO.......", encode=True)
    # display_text = set_display_text(ser, 1, "POR FAVOR ESPERE", encode=True)
    ser = 3
    async with websockets.connect(
        'ws://localhost:9000/CP_1', 
        # 'wss://6fdd23de.ngrok.io/proyectoD2V',
        # 'ws://movilidadelectricadev.corp.ute.com.uy/CentralSystemOCPP16J/WebSocketHandler.ashx/proyectoD2V',
        subprotocols=['ocpp1.6']
    ) as ws:

        #Init chargePoint
        cp = ChargePoint('proyectoD2V', ws)
        
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
                boot_heartbeat(cp, ser, c_p_model, c_p_vendor),
                # full_charge(cp, ser, ws, vc),
                # cp.send_boot_notification(c_p_model, c_p_vendor),
                # cp.send_authorize(tag_rfid),
                # cp.send_heartbeat(),
                # evse_status(ser)
                # cp.send_change_availability(con_id, av_type),
                # cp.send_start_transaction(con_id, tag_rfid, global_energy, time_string)
                )

if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
