import asyncio
import sys
import datetime
from aiomeshtastic import bt_connection


async def main(connetion_string):
    if connetion_string == "__first__":
        device = await bt_connection.find_first_device()
    else:
        device = await bt_connection.find_by_name(connetion_string)
    connection = await bt_connection.BTConnection.connect(device)

    async for log in connection.stream_logs():
        ts = datetime.datetime.utcfromtimestamp(log.time)
        print(f"{ts} [{log.source}] {log.message}", end="")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
