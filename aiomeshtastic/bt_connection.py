import asyncio
from types import TracebackType
from typing import AsyncIterator, Type
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice


SERVICE = "6ba1b218-15a8-461f-9fa8-5dcae273eafd"
FROM_RADIO = "2c55e69e-4993-11ed-b878-0242ac120002"
TO_RADIO = "f75c76d2-129e-4dad-a1dd-7866124401e7"
CURRENT_PACKET_NUM = "ed9da18c-a800-4f66-a670-aa7547e34453"


class BTConnection:
    def __init__(self, client: BleakClient, name: str):
        self._name = name
        self._client = client
        self._stop = False
        self._read_ready = asyncio.Event()

    def __repr__(self) -> str:
        return f"BTConnection<{self._name}>"

    @classmethod
    async def connect(cls, device: BLEDevice) -> "BTConnection":
        client = BleakClient(device)
        await client.connect()
        return cls(client, device.name or "unk")

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def read(self) -> AsyncIterator[bytes]:
        await self._client.start_notify(
            CURRENT_PACKET_NUM, lambda _, __: self._read_ready.set()
        )

        while not self._stop:
            while data := await self._client.read_gatt_char(FROM_RADIO):
                yield bytes(data)
            await self._read_ready.wait()
            self._read_ready.clear()

    async def write(self, msg: bytes) -> None:
        await self._client.write_gatt_char(TO_RADIO, msg, response=False)


async def find_first_device() -> BLEDevice:
    device = None
    async with BleakScanner(service_uuids=[SERVICE]) as scanner:
        async for device, data in scanner.advertisement_data():
            return device
    assert False


async def find_by_name(name: str) -> BLEDevice:
    device = None
    async with BleakScanner(service_uuids=[SERVICE]) as scanner:
        async for device, data in scanner.advertisement_data():
            if data.local_name == name:
                return device
    assert False
