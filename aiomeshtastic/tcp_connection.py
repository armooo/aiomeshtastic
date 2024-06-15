import asyncio

from . import stream_connection


class TCPConnection(stream_connection.Connection):
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        host: str,
        port: int,
    ) -> None:
        stream_connection.Connection.__init__(self, reader, writer)
        self._host = host
        self._port = port

    def __repr__(self) -> str:
        return f"TCPConnection<{self._host}:{self._port}>"

    @classmethod
    async def connect(self, host: str, port: int) -> "TCPConnection":
        reader, writer = await asyncio.open_connection(host, port)
        return TCPConnection(reader, writer, host, port)
