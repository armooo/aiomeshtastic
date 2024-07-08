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
        conn = TCPConnection(reader, writer, host, port)
        conn.start_keepalive()
        return conn

    async def disconnect(self) -> None:
        self.stop_keepalive()
        await stream_connection.Connection.disconnect(self)
