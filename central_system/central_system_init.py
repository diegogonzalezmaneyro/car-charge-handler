import asyncio
import websockets
from datetime import datetime

from ocpp.routing import on, after
from ocpp.v16 import call_result, ChargePoint as cp
# from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus
from ocpp.v16.enums import *

#as do not use database, implement an array were you can find
#all the valid tokens
valid_tokens = [1234,12345,1111,2222]

class ChargePoint(cp):
    # ### START TEMPLATE ##
    # @on(Action.ACTION_NAME)
    # def on_ACTION_NAME(self, VARS):
    #     return call_result.ACTION_NAME(
    #         current_time=datetime.utcnow().isoformat(),
    #         interval=10,
    #         status=RegistrationStatus.accepted
    #     )

    # @after(Action.ACTION_NAME)
    # def after_ACTION_NAME(self, VARS):
    #     print("SOMETHING TO PRINT")
    # ### END TEMPLATE ##

    ## START ACTIONS ##
    ################## BOOT NOTIFICATION ##########################
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=5,
            status=RegistrationStatus.accepted
        )

    @after(Action.BootNotification)
    def after_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        print("Boot Notification from:")
        print("ChargePoint Vendor: ", charge_point_vendor)
        print("ChargePoint Model: ",charge_point_model)

    ################## HEARTBEAT ##########################
    @on(Action.Heartbeat)
    def on_heartbeat(self):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat()
        )

    @after(Action.Heartbeat)
    def after_heartbeat(self):
        print("Heartbeat: ", datetime.utcnow().isoformat())

    ################## AUTHORIZE ##########################
    @on(Action.Authorize)
    def on_authorize(self, id_tag):
        if int(id_tag) in valid_tokens:
            return call_result.AuthorizePayload(
                id_tag_info={
                    "status" : AuthorizationStatus.accepted
                }
            )
        else:
            return call_result.AuthorizePayload(
                id_tag_info={
                    "status" : AuthorizationStatus.invalid
                }
            )

    @after(Action.Authorize)
    def after_authorize(self, id_tag):
        print("Authorization requested from: ", id_tag)

    ################## START TRANSACTION ##########################
    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp):
        trans_id = 987
        return call_result.StartTransactionPayload(
            transaction_id = trans_id,
            id_tag_info={
                "status" : AuthorizationStatus.accepted
            }
        )

    @after(Action.StartTransaction)
    def after_stop_transaction(self, meter_value_stop, trans_id, timest):
        print("Started transaction in connector {}, from {}, starting meter: {}, timestamp {}".format(connector_id, id_tag, meter_start, timestamp))

    ################## METER VALUES ##########################
    @on(Action.MeterValues)
    def on_meter_values(self, connector_id, meter_value):
        return call_result.MeterValuesPayload(
        )

    @after(Action.MeterValues)
    def after_meter_values(self, connector_id, meter_value):
        print("Received meter values from ", connector_id)

    ################## STOP TRANSACTION ##########################
    @on(Action.StopTransaction)
    def on_stop_transaction(self, meter_stop, timestamp, transaction_id):
        return call_result.StopTransactionPayload(
            # id_tag_info={
            #     "status" : AuthorizationStatus.accepted
            # }
        )

    @after(Action.StopTransaction)
    def after_stop_transaction(self, meter_stop, timestamp, transaction_id):
        print("Stop transaction ", transaction_id )
    
    @on(Action.ChangeAvailability)
    def on_change_avilability(self, connector_id, av_type):
        return call_result.ChangeAvailabilityPayload(
            status=AvailabilityStatus.accepted
        )


    @after(Action.ChangeAvailability)
    def after_change_avilability(self, connector_id, type):
        print("Change avilability ready")


async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """
    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        # '192.168.1.7',
        9000,
        subprotocols=['ocpp1.6']
    )

    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())