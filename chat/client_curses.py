import socket
from curses import newwin, wrapper
from curses.ascii import isprint
from threading import Thread

from chat import helper

def handleRecv(sock, separator, stdscr, textbox):
    height, width = stdscr.getmaxyx()
    centerX = width // 2
    msgPosition = height - 8
    leftLine = 3

    while True:
        textbox.border()
        if msgPosition < 3:
            msgPosition = height - 8
            stdscr.clear()
            textbox.border()

        data = helper.receiver(sock)
        if not data:
            break

        msgSplited = data.split(separator)
        msgSplitLen = len(msgSplited)

        if msgSplitLen == 3:
            # server, clientName, msg  (legacy fallback)
            server, clientName, msg = msgSplited
            stdscr.addstr(msgPosition, centerX, f"{clientName} {msg}")
        elif msgSplitLen == 2:
            name, msg = msgSplited
            stdscr.addstr(msgPosition, 0, f"{name}: {msg}")
        else:
            # try JSON parse
            try:
                j = helper.jsonExt(data)
                if "name" in j and "data" in j:
                    stdscr.addstr(msgPosition, 0, f"{j['name']}: {j['data']}")
                elif "name" in j and "event" in j:
                    stdscr.addstr(msgPosition, centerX, f"{j['name']} {j['event']}")
            except Exception:
                pass

        stdscr.refresh()
        msgPosition -= leftLine

def wrap(text, width):
    listOfWord = []
    totalLen = len(text)
    idx = 0
    part = ""
    for ch in text:
        part += ch
        idx += 1
        if idx % width == 0:
            listOfWord.append(part)
            part = ""
    if part:
        listOfWord.append(part)
    return listOfWord

def main(stdscr):
    host = helper.HOST
    port = helper.PORT
    separator = helper.SEPARATOR
    close = helper.CLOSE_TOKEN

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Cannot connect:", e)
        return

    name = input("Enter Name: ")
    helper.sender(sock, helper.jsonBuilder(name=name))

    height, width = stdscr.getmaxyx()
    inputList = []
    boxHeight = 5
    winHeight = height - boxHeight
    maxWidth = width - 2
    maxText = (boxHeight - 2) * maxWidth
    textbox = newwin(boxHeight, width - 2, winHeight, 1)
    textbox.border()
    textbox.addstr(1, 1, "")

    handler = Thread(target=handleRecv, args=(sock, separator, stdscr, textbox))
    handler.daemon = True
    handler.start()

    while True:
        textbox.refresh()
        try:
            char = textbox.getch()
        except KeyboardInterrupt:
            break

        if char == 10:  # Enter
            if inputList:
                data = "".join(inputList)
                textbox.clear()
                textbox.border()
                inputList.clear()

                helper.sender(sock, data)
                if data == close:
                    break
            else:
                continue
        elif char in (8, 127):  # Backspace/Delete
            if inputList:
                inputList.pop()
                textbox.clear()
                textbox.border()
        elif isprint(char) and len("".join(inputList)) < maxText:
            inputList.append(chr(char))

        msg = "".join(inputList)
        msgSplited = wrap(msg, maxWidth)
        msgLen = len(msgSplited)

        if msgLen == 0:
            textbox.addstr(1, 1, "")
            continue

        for line in range(msgLen):
            textbox.addstr(line + 1, 1, msgSplited[line])

wrapper(main)
