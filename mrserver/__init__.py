"""A simple chat server created using Websocket protocol.

This a simple chat server which uses the Websocket protocol
to connect with clients and relay information back and forth.
The server has a list of events and payload protocols every
client must adhere to. There is also a special handshake in place
that takes place before any other communication.
"""


from .server import Server

__all__ = ["Server"]

__author__ = "Anish Jewalikar"
__license__ = "MIT"
__version__ = "0.1.0"
