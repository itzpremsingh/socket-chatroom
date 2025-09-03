import re
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from typing import Dict, List

from chat import helper

# pattern to detect private messages like "<name> message"
PRIVATE_PATTERN = re.compile(r"^\s{0,}<(.+)>\s{0,}(.*)\s{0,}$")

def sendToAll(clientList: List, msg: str, senderClient) -> None:
    """Send msg to every client except senderClient."""
    for c in clientList:
        if c is not senderClient:
            try:
                helper.sender(c, msg)
            except Exception:
                # ignore broken clients here; they will be cleaned later
                pass

def handleClient(client, clientList: List, clientDict: Dict[str, object]) -> None:
    """Handle a single client connection."""
    data = helper.receiver(client)
    if not data:
        client.close()
        return

    try:
        jsonData = helper.jsonExt(data)
        name = jsonData.get("name")
    except Exception:
        client.close()
        return

    if not name:
        client.close()
        return

    clientDict[name] = client
    print(helper.center(f"{name} Joined", helper.MSG_COLOR))

    # announce join
    sendToAll(clientList, helper.jsonBuilder(name=name, event="Joined"), client)

    while True:
        data = helper.receiver(client)
        if not data:
            break
        if data == helper.CLOSE_TOKEN:
            break

        match = PRIVATE_PATTERN.match(data)
        if match:
            to_name, msg = match.groups()
            target = clientDict.get(to_name)
            if target:
                try:
                    helper.sender(target, helper.jsonBuilder(by=name, data=msg))
                    print(f"{helper.RECV_COLOR}{name} to {to_name}: (private)")
                except Exception:
                    pass
            else:
                # inform sender that target not found
                try:
                    helper.sender(client, helper.jsonBuilder(event=f"User {to_name} not found"))
                except Exception:
                    pass
        else:
            # broadcast
            sendToAll(clientList, helper.jsonBuilder(name=name, data=data), client)
            print(f"{helper.RECV_COLOR}{name}: {data}\33[m")

    # cleanup
    sendToAll(clientList, helper.jsonBuilder(name=name, event="Left"), client)
    print(helper.center(f"{name} Left", helper.MSG_COLOR))
    try:
        clientList.remove(client)
    except ValueError:
        pass
    client.close()
    clientDict.pop(name, None)


def runServer(host: str = helper.HOST, port: int = helper.PORT) -> None:
    """Start the chat server."""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(1, 2, 1)  # allow reuse (platform dependent)
    sock.bind((host, port))
    sock.listen(10)
    print("Chat server started on", host, port)

    clientList: List = []
    clientDict: Dict[str, object] = {}

    try:
        while True:
            client, _addr = sock.accept()
            clientList.append(client)
            handler = Thread(target=handleClient, args=(client, clientList, clientDict))
            handler.daemon = True
            handler.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        for c in list(clientList):
            try:
                helper.sender(c, helper.CLOSE_TOKEN)
                c.close()
            except Exception:
                pass
        sock.close()

if __name__ == "__main__":
    runServer()
