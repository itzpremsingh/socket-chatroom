from json import dumps, loads
from os import get_terminal_size
from typing import Any

HOST = "127.0.0.1"
PORT = 8000
RECV_SIZE = 2048
MSG_COLOR = "\33[100m"
RECV_COLOR = "\33[34m"
SEPARATOR = "<seprater>"
CLOSE_TOKEN = "<close-connection>"

def jsonBuilder(**data: Any) -> str:
    """Build JSON string from kwargs."""
    return dumps(data)

def jsonExt(data: str) -> dict:
    """Parse JSON string to dict."""
    return loads(data)

def sender(sock, data: str | bytes, encode: bool = True) -> bytes:
    """
    Send data over socket.
    - If encode is True and data is str, send bytes.
    - Uses sendall for reliability.
    Returns sent bytes.
    """
    if isinstance(data, str) and encode:
        data_bytes = data.encode()
    elif isinstance(data, bytes):
        data_bytes = data
    else:
        data_bytes = str(data).encode()
    sock.sendall(data_bytes)
    return data_bytes

def receiver(client, recv: int = RECV_SIZE) -> str | None:
    """Receive data from socket and decode. Return None on empty recv."""
    try:
        data = client.recv(recv)
    except ConnectionResetError:
        return None
    if not data:
        return None
    try:
        return data.decode()
    except Exception:
        return None

def center(string: str, color: str = "") -> str:
    """Return centered string for terminal width with optional color."""
    width = get_terminal_size().columns
    space = max(0, width // 2 - len(string) // 2)
    return f"{' ' * space}{color}{string}\33[m"
