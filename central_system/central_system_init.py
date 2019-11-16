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
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @after(Action.BootNotification)
    def after_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        print("ChargePoint Vendor is: ", charge_point_vendor)
        print("ChargePoint Model is: ",charge_point_model)

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
        print("authorization of ", id_tag)

    @on(Action.ChangeAvailability)
    def on_change_avilability(self, connector_id, av_type):
        return call_result.ChangeAvailabilityPayload(
            status=AvailabilityStatus.accepted
        )

    @after(Action.ChangeAvailability)
    def after_change_avilability(self, connector_id, type):
        print("Change avilability ready")

    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp):
        trans_id = 666
        return call_result.StartTransactionPayload(
            transaction_id = trans_id,
            id_tag_info={
                "status" : AuthorizationStatus.accepted
            }
        )

    @after(Action.StartTransaction)
    def after_start_transaction(self, connector_id, id_tag, meter_start, timestamp):
        print("STARTED transaction in connector {}, from {}, starting meter: {}, timestamp {}".format(connector_id, id_tag, meter_start, timestamp))

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
        9000,
        subprotocols=['ocpp1.6']
    )

    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())