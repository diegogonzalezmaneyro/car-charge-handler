import asyncio
from ocpp.routing import on, after
from ocpp.v16 import call, call_result, ChargePoint as cp
from ocpp.v16.enums import *
import time

class ChargePoint(cp):

    ################## BOOT NOTIFICATION ##########################
    async def send_boot_notification(self, c_p_model, c_p_vendor):
        await asyncio.sleep(1)

        request = call.BootNotificationPayload(
            charge_point_model = c_p_model,
            charge_point_vendor = c_p_vendor
        )
        response = await self.call(request)

        if response.status ==  RegistrationStatus.accepted:
            print("Connected to central system.")
            hb = response.interval
            print("Heartbeat changed to ", hb," seconds")
            return(hb)
        else:
            print("Not connected to central system")

    ################## HEARTBEAT ##########################
    async def send_heartbeat(self):

        request = call.HeartbeatPayload()

        response = await self.call(request)

        if response.current_time:
            print("Heartbeat delivered: ", response.current_time)
        else:
            print("Heartbeat not delivered")
        
    ################## AUTHORIZE ##########################
    async def send_authorize(self, id_tag_rfid):
        
        request = call.AuthorizePayload(
            id_tag = id_tag_rfid
        )

        response = await self.call(request)

        if response.id_tag_info['status'] ==  RegistrationStatus.accepted:
            print(" Authorizated by central system.")
            return True
        else:
            print("For some reason we are out, go home kid")
            return False

    ################## START TRANSACTION ##########################
    async def send_start_transaction(self, charge_status, meter, timest):

        request = call.StartTransactionPayload(
            connector_id = charge_status.connector_id,
            id_tag = charge_status.rfid,
            meter_start = meter,
            timestamp = timest
            # reservation_id = res_id ### Optional
        )

        response = await self.call(request)
        if response.id_tag_info['status'] ==  AuthorizationStatus.accepted:
            print("Start transaction ACCEPTED")
            return response.transaction_id, True
        else:
            print("Transaction failed")
            return 0, False

    ################## METER VALUES ##########################
    async def send_meter_values(self, connector, timestamp, met_value):
        meter_array = []
        meter_array.append({
        "timestamp": timestamp,
        "sampledValue": [
            {"value":met_value}]
        })
        request = call.MeterValuesPayload(
            connector_id = connector,
            meter_value = list(meter_array)
            # transaction_id = int ### Optional
        )
        response = await self.call(request)

        if response:
            print("Meter values sent")
        else:
            print("Error in central system with meter values")

    ################## STOP TRANSACTION ##########################
    async def send_stop_transaction(self, meter_value_stop, timest, trans_id):

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
            #return False to turn off transaction status
            return False
        else:
            print("Error Stopping transaction")
            return True
          
    ############# REMOTE START TRANSACTION ##################
    @on(Action.RemoteStartTransaction)
    def on_remote_start_transaction(self, id_tag):
        print('START aceptado de id: ',id_tag)
        return call_result.RemoteStartTransactionPayload(
            status=RemoteStartStopStatus.accepted
        )
    
    @after(Action.RemoteStartTransaction)
    def after_remote_start_transaction(self, id_tag):
        
        line_to_save = '{};{}\n'.format(id_tag,time.time())
        with open('rfid_inputs.txt', 'a') as file:
            file.write(line_to_save)

    ############# REMOTE STOP TRANSACTION ##################
    @on(Action.RemoteStopTransaction)
    def on_remote_stop_transaction(self, transaction_id):
        print('STOP aceptado para transaccion: ',transaction_id)
        return call_result.RemoteStopTransactionPayload(
            status=RemoteStartStopStatus.accepted
        )

    @after(Action.RemoteStopTransaction)
    def after_remote_stop_transaction(self, transaction_id):
        
        line_to_save = '{};{}\n'.format(transaction_id,time.time())
        with open('rfid_inputs.txt', 'a') as file:
            file.write(line_to_save)

