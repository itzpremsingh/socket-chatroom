# CLI Chat with Curses Support

A simple command line chat application with curses support.

## Features

- Multi-user chat
- Private messages
- Server and client support
- Curses support for better user experience

## Usage

### Server

- Run the application with `python main.py server`
- The server will start on localhost:8000
- The server will broadcast messages to all connected clients

### Client

- Run the application with `python main.py client`
- The client will connect to the server on localhost:8000
- The client will send messages to the server which will be broadcasted to all connected clients

### Curses Client

- Run the application with `python main.py curses`
- The curses client will connect to the server on localhost:8000
- The curses client will use the entire terminal to display messages and allow the user to input messages

## License

This project is licensed under the MIT License.
