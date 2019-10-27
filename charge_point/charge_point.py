import asyncio
import websockets

from ocpp.v16 import call, ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus


class ChargePoint(cp):
    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="Optimus",
            charge_point_vendor="The Mobility House"
        )

        response = await self.call(request)

        if response.status ==  RegistrationStatus.accepted:
            print("Connected to central system.")
        else:
            print("Registration denied")

async def main():
    async with websockets.connect(
        'ws://localhost:9000/CP_1',
         subprotocols=['ocpp1.6']
    ) as ws:

        cp = ChargePoint('CP_1', ws)

        await asyncio.gather(cp.start(), cp.send_boot_notification())


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

