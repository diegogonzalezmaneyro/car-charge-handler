import asyncio
import websockets

from ocpp.v16 import call, ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus


class ChargePoint(cp):
    async def send_boot_notification(self, c_p_model, c_p_vendor):
        request = call.BootNotificationPayload(
            charge_point_model=c_p_model,
            charge_point_vendor=c_p_vendor
        )

        response = await self.call(request)

        if response.status ==  RegistrationStatus.accepted:
            print("Connected to central system.")

    async def send_authorize(self, idTagRfid):
        request = call.AuthorizePayload(
            id_tag=idTagRfid
        )

        response = await self.call(request)

        if response.id_tag_info['status'] ==  RegistrationStatus.accepted:
            print("Connected to central system.")
        else:
            print("For some reason we are out, go home kid")

async def main():
    async with websockets.connect(
        'ws://localhost:9000/CP_1',
         subprotocols=['ocpp1.6']
    ) as ws:

        #Init chargePoint
        cp = ChargePoint('CP_1', ws)
        
        #Boot nofitication step
        c_p_model = "openEVSE-D2V"
        c_p_vendor = "Pura Cepa"
        
        #Authorize
        tag_rfid = str(9876)
        await asyncio.gather(cp.start(), cp.send_boot_notification(c_p_model, c_p_vendor),cp.send_authorize(tag_rfid))



if __name__ == '__main__':
    asyncio.run(main())
