from socket import AF_INET, SOCK_STREAM, socket
from sys import argv
from threading import Thread

from chat import helper

def handleRecv(sock):
    """Thread: receive server messages and print nicely."""
    while True:
        data = helper.receiver(sock)
        if not data:
            print("\nDisconnected by server.")
            break

        try:
            jsonData = helper.jsonExt(data)
        except Exception:
            continue

        senderName = jsonData.get("name")
        payload = jsonData.get("data")
        event = jsonData.get("event")
        directBy = jsonData.get("by")

        # move cursor up and clear current input line
        print("\033[F", end="\033[K")

        if not senderName and directBy:
            senderName = "<direct> " + directBy

        if payload:
            print(f"{helper.RECV_COLOR}{senderName}: {payload}\33[m")
        elif event:
            print(helper.center(f"{senderName} {event}", helper.MSG_COLOR))
        else:
            print(helper.center("Unknown message", helper.MSG_COLOR))

        print("Enter Message: ", end="", flush=True)


def main():
    # get name from argv or prompt
    if len(argv) > 1:
        name = argv[1]
    else:
        try:
            name = input("Enter Name: ")
        except (KeyboardInterrupt, Exception):
            return

    host = helper.HOST
    port = helper.PORT

    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Could not connect:", e)
        return

    # send join JSON
    helper.sender(sock, helper.jsonBuilder(name=name))

    # start receiver thread
    handler = Thread(target=handleRecv, args=(sock,))
    handler.daemon = True
    handler.start()

    try:
        while True:
            try:
                data = input("Enter Message: ")
            except (KeyboardInterrupt, EOFError):
                helper.sender(sock, helper.CLOSE_TOKEN)
                print("\nDisconnected!")
                break

            if data == "":
                continue

            # send message (raw or private syntax)
            try:
                helper.sender(sock, data, encode=True)
            except BrokenPipeError:
                print("Server closed!")
                break

            if data == helper.CLOSE_TOKEN:
                break
    finally:
        try:
            sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
