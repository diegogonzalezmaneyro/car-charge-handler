#!/usr/bin/env python

import asyncio
import websockets

async def remote_start(ws):
    idtag_remote = await ws.recv()
    print("< {}".format(idtag_remote))
    
async def main(): 

    async with websockets.connect(
        'ws://localhost:9000/CP_1', 
         subprotocols=['ocpp1.6']
    ) as ws:

        await asyncio.gather(
            remote_start(ws)
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
