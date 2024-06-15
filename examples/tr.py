import sys
import asyncio
import random
import webbrowser

from aiomeshtastic import get_client

from meshtastic.mesh_pb2 import ToRadio, MeshPacket, RouteDiscovery
from meshtastic.portnums_pb2 import PortNum


async def main() -> None:
    connect_string = sys.argv[1]
    node_id = int(sys.argv[2][1:], 16)
    packet_id = random.getrandbits(32)

    async with get_client(connect_string) as client:
        await client.get_config()
        tr = ToRadio()
        tr.packet.decoded.portnum = PortNum.TRACEROUTE_APP
        tr.packet.decoded.want_response = True
        tr.packet.id = packet_id
        tr.packet.to = node_id
        tr.packet.hop_limit = 7
        tr.packet.hop_start = 7
        print(tr)
        await client.write(tr)

        await asyncio.sleep(5)

        webbrowser.open(f"https://meshview.armooo.net/graph/traceroute/{packet_id}")

        try:
            async with asyncio.timeout(30):
                async for fr in client.read():
                    if fr.packet.decoded.request_id == packet_id:
                        print(RouteDiscovery.FromString(fr.packet.decoded.payload))
                        break
        except TimeoutError:
            print("Traceroute took too long")
            sys.exit(1)


asyncio.run(main())
