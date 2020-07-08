import asyncio
import json
import logging
import typing
import uuid

import websockets
from colorama import Fore

FUNCTION_MAP = {"CREATE_MESSAGE": "create_message"}


class ClientModel:
    """Represents a user who is connected to the server."""

    def __init__(
        self, cid: str, name: str, ws: websockets.WebSocketServerProtocol
    ) -> None:

        self.cid = cid
        self.name = name
        self.ws = ws


class Server:
    """Server for message-relay application.

    This is the server for the message-relay application
    to be used in conjunction with the message-relay client.
    """

    def __init__(
        self, port: int, max_clients: int, loop: asyncio.AbstractEventLoop = None
    ) -> None:

        # Server configuration options.
        self.port = port
        self.max_clients = max_clients
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.server = None

        # Logger setup
        log_string = (
            f"{Fore.RED}[SERVER]{Fore.RESET} "
            f"{Fore.BLUE}Time: %(asctime)s{Fore.RESET} "
            f"{Fore.YELLOW}Message: %(message)s {Fore.RESET} "
        )
        logging.basicConfig(format=log_string, datefmt="%d-%b-%y %H:%M:%S")
        self.logger = logging.getLogger("PyChat Server")
        self.logger.setLevel(10)

        # Server state variables
        self.clients: typing.List[ClientModel] = []

    async def notify_new_connect(self, client: ClientModel) -> None:
        """Notify all connected clients of the connection of a new member."""

        payload = {
            "op": "NEW_MEMBER",
            "message": {"client": {"id": client.cid, "name": client.name}},
        }

        jsonified = json.dumps(payload)

        await asyncio.wait([x.ws.send(jsonified) for x in self.clients])

    async def create_message(self, client: ClientModel, message: str) -> None:
        """This creates a message object and sends that to every client."""

        payload = {
            "op": "NEW_MESSAGE",
            "message": {
                "client": {"id": client.cid, "name": client.name},
                "content": message,
            },
        }

        jsonified = json.dumps(payload)

        await asyncio.wait([x.ws.send(jsonified) for x in self.clients])

    async def parse_operation(self, client: ClientModel, payload: str) -> None:
        """Parse the operation sent by a client. Silently disregard a error."""

        request = json.loads(payload)

        op = request["op"]
        message = request["message"]
        func = getattr(self, FUNCTION_MAP[op], None)

        if func is not None:
            await func(client, message)

    async def perform_handshake(
        self, ws: websockets.WebSocketServerProtocol
    ) -> typing.Optional[ClientModel]:
        """Perform a special handshake with the client."""

        payload = {"op": "HELLO", "message": "ALLOWED"}

        # If client limit has been reached send DISLLOWED,
        # and close the websocket connection.
        if len(self.clients) == self.max_clients:
            payload["message"] = "DISALLOWED"
            await ws.send(json.dumps(payload))
            await ws.close()
            return None

        # Send ALLOWED.
        await ws.send(json.dumps(payload))

        # Wait for the client to respond,
        # with the username.
        message = await ws.recv()
        if isinstance(message, str):
            response = json.loads(message)

            # If the op-code is non-HELLO
            # close the websocket connection.
            if response["op"] != "HELLO":
                await ws.close()
                return None

            # Generate a new ID for the user,
            # and create a ClientModel object.
            new_id = uuid.uuid4().hex
            client = ClientModel(new_id, str(response["message"]), ws)

            # Send the assigned ID to the client,
            # and add the client to server's list
            # of connected clients.
            successful = {"op": "ID_ASSIGN", "message": new_id}
            await ws.send(json.dumps(successful))
            self.clients.append(client)
        else:
            return None

        await self.notify_new_connect(client)
        return client

    def cleanup_client_info(self, client: ClientModel) -> None:
        """Clean up the client information from the server."""

        try:
            self.clients.remove(client)
        except ValueError:
            self.logger.info(f"Connection anomaly {client.ws.remote_address}.")

    async def ws_handler(
        self, ws: websockets.WebSocketServerProtocol, path: str
    ) -> None:
        """Handle new incoming websocket connections from clients."""

        self.logger.info(f"Connection Established {ws.remote_address}.")

        # Check if the hanshake was performed successfully.
        client = await self.perform_handshake(ws)
        if client is None:
            return

        try:

            # If the handshake was performed succesfully,
            # keep the connection alive.
            async for payload in ws:

                if isinstance(payload, str):
                    await self.parse_operation(client, payload)
        finally:
            # After disconnecting clean up client information.
            self.cleanup_client_info(client)
            self.logger.info(f"Connection Closed {ws.remote_address}.")

    async def start(self) -> None:
        """Start the server and listen for websocket connections."""

        self.logger.info("Server Initializing.")
        self.server = await websockets.serve(
            self.ws_handler, "localhost", self.port, loop=self.loop
        )
        self.logger.info("Server successfully initialized. Waiting for clients.")

    def close(self) -> None:
        """Closes the server and cleans up the server state."""

        # Close the server and clear the client list.
        self.logger.info("Shutting down server.")
        self.server.close()
        self.clients.clear()
        self.logger.info("Server has successfully shut down.")

    def run(self) -> None:
        """A blocking call that initializes the event loop and starts the server."""

        loop = self.loop

        try:
            loop.run_until_complete(self.start())
            loop.run_forever()
        except KeyboardInterrupt:
            self.logger.info("Keyboard Interrupt encountered.")
        finally:
            self.close()
            loop.stop()
