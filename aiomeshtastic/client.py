import asyncio
import random
from types import TracebackType
from typing import AsyncIterator, Type
from typing import Protocol

from meshtastic.mesh_pb2 import ToRadio
from meshtastic.mesh_pb2 import FromRadio
from meshtastic.portnums_pb2 import PortNum
from meshtastic.telemetry_pb2 import Telemetry


class Connection(Protocol):
    async def disconnect(self) -> None:
        ...

    def read(self) -> AsyncIterator[bytes]:
        ...

    async def write(self, msg: bytes) -> None:
        ...


class Client:
    def __init__(self, connection: Connection) -> None:
        self._connecion = connection
        self._stop = False

    def __repr__(self) -> str:
        return f"Client<{self._connecion!r}>"

    async def read(self) -> AsyncIterator[FromRadio]:
        while not self._stop:
            async for msg in self._connecion.read():
                yield FromRadio.FromString(msg)

    async def write(self, proto: ToRadio) -> None:
        await self._connecion.write(proto.SerializeToString())

    async def get_config(self) -> list[FromRadio]:
        nonce = random.randint(0, 2**32)
        config = []
        await self.write(ToRadio(want_config_id=nonce))
        async for proto in self.read():
            if proto.config_complete_id == nonce:
                break
            config.append(proto)
        return config
