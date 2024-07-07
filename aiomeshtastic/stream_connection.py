import asyncio
from types import TracebackType
from typing import AsyncIterator, Type

from meshtastic.mesh_pb2 import ToRadio, Heartbeat

MAGIC = b"\x94\xC3"


class Connection:
    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self._stop = False
        self._reader = reader
        self._writer = writer
        self._keepalive_task: asyncio.Task[None] | None = None

    async def disconnect(self) -> None:
        assert self._writer
        self._writer.close()
        await self._writer.wait_closed()

    async def read(self) -> AsyncIterator[bytes]:
        assert self._reader
        while not self._stop:
            await self._reader.readuntil(MAGIC)
            proto_len = int.from_bytes(await self._reader.readexactly(2), "big")
            yield await self._reader.readexactly(proto_len)

    async def write(self, msg: bytes) -> None:
        self._writer.write(MAGIC)
        self._writer.write(len(msg).to_bytes(2, "big", signed=False))
        self._writer.write(msg)
        await self._writer.drain()

    def start_keepalive(self) -> None:
        self._keepalive_task = asyncio.create_task(self._keepalive())

    def stop_keepalive(self) -> None:
        if self._keepalive_task is not None:
            self._keepalive_task.cancel()

    async def _keepalive(self) -> None:
        while True:
            await asyncio.sleep(60)
            tr = ToRadio()
            tr.heartbeat.CopyFrom(Heartbeat())
            await self.write(tr.SerializeToString())
