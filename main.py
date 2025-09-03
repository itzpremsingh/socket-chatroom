from sys import argv

def main():
    if len(argv) < 2:
        print("Usage: python main.py [server|client|curses]")
        return

    mode = argv[1].lower()

    if mode == "server":
        from chat.server import runServer
        runServer()
    elif mode == "client":
        from chat.client import main as clientMain
        clientMain()
    elif mode == "curses":
        from chat.client_curses import wrapper, main as cursesMain
        wrapper(cursesMain)
    else:
        print("Unknown mode:", mode)
        print("Use: server | client | curses")

if __name__ == "__main__":
    main()
