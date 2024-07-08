import asyncio

import serial_asyncio  # type: ignore

from . import stream_connection


class SerialConnection(stream_connection.Connection):
    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, path: str
    ) -> None:
        stream_connection.Connection.__init__(self, reader, writer)
        self._path = path

    def __repr__(self) -> str:
        return f"SerialConnection<{self._path}>"

    @classmethod
    async def connect(cls, path: str) -> "SerialConnection":
        reader, writer = await serial_asyncio.open_serial_connection(
            url=path,
            baudrate=115200,
        )
        conn = SerialConnection(reader, writer, path)
        conn.start_keepalive()
        return conn

    async def disconnect(self) -> None:
        self.stop_keepalive()
        await stream_connection.Connection.disconnect(self)
