import asyncio
from ocpp.v16 import call, ChargePoint as cp
from ocpp.v16.enums import *

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
        global AUTHORIZED
        request = call.AuthorizePayload(
            id_tag = id_tag_rfid
        )

        response = await self.call(request)

        if response.id_tag_info['status'] ==  RegistrationStatus.accepted:
            AUTHORIZED = True
            print("Authorizated by central system.")
        else:
            AUTHORIZED = False
            print("For some reason we are out, go home kid")

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
