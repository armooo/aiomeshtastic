import contextlib
from typing import Protocol
from urllib.parse import urlparse
from types import TracebackType
from typing import AsyncIterator, Type

from .bt_connection import BTConnection
from .client import Client, Connection
from .serial_connection import SerialConnection
from .tcp_connection import TCPConnection
from . import bt_connection


async def connect(connetion_string: str) -> Connection:
    url = urlparse(connetion_string)
    print(url)
    if url.scheme == "serial":
        return await SerialConnection.connect(url.path)
    elif url.scheme == "bt":
        if url.netloc == "__first__":
            device = await bt_connection.find_first_device()
        else:
            device = await bt_connection.find_by_name(url.netloc)
        return await BTConnection.connect(device)
    elif url.scheme == "tcp":
        if ":" in url.netloc:
            host, port_str = url.netloc.split(":")
            port = int(port_str)
        else:
            host = url.netloc
            port = 4403
        return await TCPConnection.connect(host, port)
    else:
        raise AttributeError


@contextlib.asynccontextmanager
async def get_client(connetion_string: str) -> AsyncIterator[Client]:
    connection = await connect(connetion_string)
    yield Client(connection)
    await connection.disconnect()


__all__ = [
    "Client",
    "Connection",
    "connect",
    "get_client",
]
