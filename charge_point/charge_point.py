import asyncio
import websockets
from datetime import datetime
import time

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
        # Send Boot notification only when the equipment is energizd:
        # ---> Charge point model (seted at start)
        # ---> Charge point vendor (seted at start)
        # Response: Check if "status" = ACCEPTED
        # Save into HEARTBEAT_INTERVAL to set the heart beat interval

    #HEART BEAT
        # Send hert beat without info, just like a ping.
        # It may be used the time response to sync with the equipment
    
    global HEARTBEAT_INTERVAL
    global CHARGING

    HEARTBEAT_INTERVAL = await cp.send_boot_notification(c_p_model, c_p_vendor)
    display_color = set_display_color(ser, 2, encode=True)
    display_text = set_display_text(ser, 0, "__CONECTADO A___", encode=True) # 0 = row 0 from display
    display_text = set_display_text(ser, 1, "SISTEMA CENTRAL_", encode=True) # 1 = row 1 from display
    
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        await cp.send_heartbeat()

####################################################################################################
#SECOND CORE FUNCTION
    #AUTHORIZE
        # Send authorize when an ID show up:
        # ---> ID tag (get from RFID input)
        # Response: check if IDTAG_info = ACCEPTED

    #START TRANSACTION
        # Send start transaction if IDTAG = accepted:
        # ---> ConnectorID = use "1" as only using one OpenEVSE
        # ---> IDTAG just used
        # ---> meter start (OpenEVSE global_energy from function get_energy_usage)
        # ---> timestamp (python lib time)
        # Resonse: IDTAG_info = ACCEPTED (must be the same)
        # Save transaction_id

    #METER VALUES
        # Send meter values every heart beat interval:
        # ---> ConnectorID = use "1" as only using one OpenEVSE
        # ---> Meter value (OpenEVSE session_energy from function get_energy_usage)
        # Response: empty

    #STOP TRANSACTION
        # Send when finish transaction
        # ---> meter stop (OpenEVSE global_energy from function get_energy_usage)
        # ---> timestamp (python lib time)
        # ---> transaction_ID (saved from start transaction)
        # Response: empty

async def full_charge(cp, ser, ws,  v_charge):
    global HEARTBEAT_INTERVAL
    global CHARGING
    
    await asyncio.sleep(10)
    
    while True:

        #############################
        ####### WAITING RFID ########
        #############################
        await asyncio.sleep(5)
        display_color = set_display_color(ser, 2, encode=True) # 2 = Green 
        display_text = set_display_text(ser, 0, "___DISPONIBLE___", encode=True) # 0 = row 0 from display
        display_text = set_display_text(ser, 1, "APROXIME TARJETA", encode=True) # 1 = row 1 from display
        send_authorize, rfid_readed = check_rfid_input()
 
        #############################
        ####### RFID RECEIVED #######
        #############################
        if send_authorize:
            v_charge.rfid = rfid_readed
            v_charge.authorize = await cp.send_authorize(v_charge.rfid)

            #############################
            ###### RFID AUTHORIZED ######
            #############################            
            if v_charge.authorize:
                # Display message to user
                display_text = set_display_text(ser, 0, "__TARJETA RFID__", encode=True) # 0 = row 0 from display
                display_text = set_display_text(ser, 1, "___AUTORIZADA___", encode=True) # 1 = row 1 from display
                await asyncio.sleep(3)

                # Get data to send start transaction
                timest = datetime.utcnow().isoformat()
                status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                status, seted_amps, flag = get_current_settings(ser, encode=True)
                v_charge.transaction_id, v_charge.transaction_status = await cp.send_start_transaction(v_charge, global_energy, timest)

                #############################
                ### TRANSACTION AUTHORIZED ##
                #############################            
                if v_charge.transaction_status:
                    # ENABLE CHARGE
                    print("enable open EVSE")
                    enable_open_EVSE = set_enable(ser,encode=ENCODER)
                    _, state, _ = get_status(ser, encode=ENCODER)
                    await asyncio.sleep(5)

                    # DO NOT START CHARGING UNTIL VEHICLE CONNECTED
                    if state != 3: # 3 = connected
                        display_color = set_display_color(ser, 3, encode=True) # 3 = Yellow
                        display_text = set_display_text(ser, 0, "____CONECTAR____", encode=True) # 0 = row 0 from display
                        display_text = set_display_text(ser, 1, "____VEHICULO____", encode=True) # 1 = row 1 from display
                        connected = False
                        while not connected:
                            await asyncio.sleep(3)
                            try:
                                _, state, _ = get_status(ser, encode=ENCODER)
                                if state == 3:
                                    connected = True
                            except:
                                pass

                    # CHANGE FLAG AND SET DISPLAY COLOR WHEN CHARGING
                    CHARGING = True
                    set_display_color(ser, color_int=6, encode=ENCODER) # 6 = Teal
                    display_text = set_display_text(ser, 0, "Charging...", encode=True) # 0 = row 0 from display

                #############################
                ####### CHARGING LOOP #######
                #############################
                while CHARGING:
                    await asyncio.sleep(5)

                    # CHECK STATUS
                    _, state, _ = get_status(ser, encode=ENCODER)
                    if state == 3: # 3 = connected
                        CHARGING = True

                        # CHECK CURRENT LIMIT
                        status, current_amps, current_volts = get_charging_data(ser, encode=True)
                        current_disable = disable_by_current(seted_amps,current_amps)
                        if current_disable:
                            disable_open_EVSE = set_disable(ser, encode=True)
                            CHARGING = False
                            display_color = set_display_color(ser, 1, encode=True) # 1 = Red
                            display_text = set_display_text(ser, 0, "EXCESO CORRIENTE", encode=True)
                            display_text = set_display_text(ser, 1, "________________", encode=True)
                            await asyncio.sleep(10)
                            break

                        # SEND METER VALUE
                        # Get data to send meter value
                        timest = datetime.utcnow().isoformat()
                        status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                        await cp.send_meter_values(v_charge.connector_id, timest, str(session_energy))
                        print("meter_values: ", session_energy)

                    # CHECK ERRORS
                    elif state in [1,4,6]: 
                        disable_open_EVSE = set_disable(ser, encode=True)
                        CHARGING = False
                        display_color = set_display_color(ser, 1, encode=True) # 1 = Red
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
                    
                    # STATE WHEN COMMUNICATION ERROR
                    elif state != 888:
                        disable_open_EVSE = set_disable(ser, encode=True)
                        CHARGING = False
                        display_color = set_display_color(ser, 1, encode=True) # 1 = Red
                        display_text = set_display_text(ser, 0, "_PUNTO DE CARGA_", encode=True)
                        display_text = set_display_text(ser, 1, "____EN FALLA____", encode=True)
                        await asyncio.sleep(10)
                        break

                    #############################
                    ####### WAITING RFID ########
                    #############################
                    send_authorize, rfid_readed = check_rfid_input()
                    if send_authorize:

                        #############################
                        ####### RFID RECEIVED #######
                        #############################
                        if (rfid_readed == v_charge.rfid) or (int(rfid_readed) == v_charge.transaction_id):
                            # FINISH CHARGE
                            disable_open_EVSE = set_disable(ser, encode=True)
                            CHARGING = False
                            display_color = set_display_color(ser, 3, encode=True) # 3 = Yellow
                            display_text = set_display_text(ser, 0, "__FIN DE CARGA__", encode=True)
                            display_text = set_display_text(ser, 1, "___EN PROCESO___", encode=True)
                            await asyncio.sleep(5)
                            break
                        else:
                            # INVALID RFID
                            display_color = set_display_color(ser, 3, encode=True) # 3 = Yellow
                            display_text = set_display_text(ser, 0, "__TARJETA RFID__", encode=True)
                            display_text = set_display_text(ser, 1, "____NO VALIDA___", encode=True)
                            await asyncio.sleep(5)
                            send_authorize = False
                            set_display_color(ser, color_int=6, encode=ENCODER) # 6 = Teal
                            display_text = set_display_text(ser, 0, "Charging...", encode=True) # 0 = row 0 from display


                #############################
                ####### WAITING RFID ########
                #############################
                while True:
                    if send_authorize:
                        v_charge.authorize = await cp.send_authorize(v_charge.rfid)
                        if v_charge.authorize:
                            # FINISH CHARGE
                            timest = datetime.utcnow().isoformat()
                            status_energy, session_energy, global_energy = get_energy_usage(ser,encode=ENCODER)
                            print("disable open EVSE")
                            v_charge.transaction_status = await cp.send_stop_transaction(global_energy, timest, v_charge.transaction_id)
                            if not v_charge.transaction_status:
                                display_color = set_display_color(ser, 2, encode=True) # 2 = Green 
                                display_text = set_display_text(ser, 0, "___TRANSACCION__", encode=True)
                                display_text = set_display_text(ser, 1, "_____EXITOSA____", encode=True)
                                await asyncio.sleep(5)
                                break
                        
                    else:
                        send_authorize, rfid_readed = check_rfid_input()
                        await asyncio.sleep(3)
                        
            # INVALID RFID
            else:
                print("The RFID number: ", v_charge.rfid, "was not authorized by central system")
                display_color = set_display_color(ser, 1, encode=True) # 1 = Red
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
    if (time.time()-float(aux[-1]))<9:
        return True,  aux[0]
    else:
        return False,  str(0)

async def main():
    #Connection usb-serial with openEVSE and disable
    ser = start_connection(SERIAL_NAME, BAUDRATE, TIMEOUT)
    disable_open_EVSE = set_disable(ser,encode=True)
    display_color = set_display_color(ser, 7, encode=True) # 7 = White 
    display_text = set_display_text(ser, 0, "INICIANDO.......", encode=True)
    display_text = set_display_text(ser, 1, "POR FAVOR ESPERE", encode=True)

    #Connection with central system using websockets
    async with websockets.connect(
        'ws://localhost:9000/CP_1', 
        # 'wss://6fdd23de.ngrok.io/CP_1',
        # 'ws://movilidadelectricadev.corp.ute.com.uy/CentralSystemOCPP16J/WebSocketHandler.ashx/CP_1',
        subprotocols=['ocpp1.6']
    ) as ws:

        #Init chargePoint
        ChargeBoxId = 'proyectoD2V'
        cp = ChargePoint(ChargeBoxId, ws)
        
        #Boot nofitication values
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
                full_charge(cp, ser, ws, vc),
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
