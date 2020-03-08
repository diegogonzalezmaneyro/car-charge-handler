import asyncio
import websockets
from datetime import datetime

from ocpp.routing import on, after
from ocpp.v16 import call, call_result, ChargePoint as cp
# from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus
from ocpp.v16.enums import *

#as do not use database, implement an array were you can find
#all the valid tokens
valid_tokens = ["a36ef7b0","1234","12345","1111","2222",987]

class ChargePoint_listener(cp):
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
            # interval=300,
            interval=3,
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
        if id_tag in valid_tokens:
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
    def after_start_transaction(self, connector_id, id_tag, meter_start, timestamp):
        print("Started transaction in connector {}, from {}, starting meter: {}, timestamp {}".format(connector_id, id_tag, meter_start, timestamp))

    ################## METER VALUES ##########################
    @on(Action.MeterValues)
    def on_meter_values(self, connector_id, meter_value):
        return call_result.MeterValuesPayload(
        )

    @after(Action.MeterValues)
    def after_meter_values(self, connector_id, meter_value):
        print("Received meter values")

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
        print("Stop transaction ", transaction_id, "meter value: ", meter_stop )

    ################## change ##########################
    @on(Action.ChangeAvailability)
    def on_change_availability(self, connector_id, av_type):
        return call_result.ChangeAvailabilityPayload(
            status=AvailabilityStatus.accepted
        )

    @after(Action.ChangeAvailability)
    def after_change_availability(self, connector_id, type):
        print("Change avilability ready")

    ################# REMOTE START TRANSACTION ##################
    async def send_remote_start_transaction(self, id_tag_cs):
        
        request = call.RemoteStartTransactionPayload(
            id_tag = id_tag_cs
        )

        response = await self.call(request)

        if response.status ==  RemoteStartStopStatus.accepted:
            print("Start remote transaction accepted from charge point!")
        else:
            print("Start remote transaction rejected from charge point!")

    ################# REMOTE END TRANSACTION ##################
    async def send_remote_end_transaction(self, transaction_id_cs):
        
        request = call.RemoteStopTransactionPayload(
            transaction_id = transaction_id_cs
        )

        response = await self.call(request)

        if response.status ==  RemoteStartStopStatus.accepted:
            print("Stop remote transaction accepted from charge point!")
        else:
            print("Stop remote transaction rejected from charge point!")


# FIRST CORE FUNCTION
async def remote_test(cp):
    # print('Start remote transaction test')
    # await asyncio.sleep(20)
    # id_tag_cs = "2222"
    # _ = await cp.send_remote_start_transaction(id_tag_cs)
    # print('remote start sended')
    #---------------------------------------------
    print('End remote transaction test')
    await asyncio.sleep(50)
    transaction_id_cs = 987
    _ = await cp.send_remote_end_transaction(transaction_id_cs)
    print('remote end sended')

async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """
    charge_point_id = path.strip('/')
    # cp = ChargePoint(charge_point_id, websocket)
    cp_created = ChargePoint_listener(charge_point_id, websocket)

    await asyncio.gather(
                cp_created.start(),
                remote_test(cp_created),
                )
    # await cp.start()
    print('after cp.start')


async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        # '192.168.1.8',
        9000,
        subprotocols=['ocpp1.6']
    )
    print('between server and wait')
    await server.wait_closed()
    print('after wait_closed')

if __name__ == '__main__':
    asyncio.run(main())