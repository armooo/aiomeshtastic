import sys
import asyncio
import random
import webbrowser

from aiomeshtastic import get_client

from meshtastic.mesh_pb2 import ToRadio, MeshPacket, RouteDiscovery
from meshtastic.portnums_pb2 import PortNum


async def main() -> None:
    connect_string = sys.argv[1]
    async with get_client(connect_string) as client:
        await client.get_config()
        async for fr in client.read():
            if fr.packet.to == 0xFFFFFFFF:
                continue
            if fr.packet.decoded.portnum != PortNum.TEXT_MESSAGE_APP:
                continue
            tr = ToRadio()
            tr.packet.to = getattr(fr.packet, 'from')
            tr.packet.decoded.portnum = PortNum.TEXT_MESSAGE_APP
            tr.packet.decoded.payload = fr.packet.decoded.payload
            await client.write(tr)


asyncio.run(main())
