# Message-Relay Server Protocol

This document describes the protocol used by the Message-Relay server to communicate with the clients.
All clients _must_ follow this protocol.

Version: **0.1.0**

## Payload

All communications to and from the server follows a fixed structure.
The server and clients send JSON encoded in a string with the following format,

```JSON
{
    op: "Operation Name",
    message: "The actual message"
}
```

Where the `op` field is a case-sensitive string, and the `message` field is either a string or another map.

## New Connection

As soon as a Websocket connection is established between the server and the client, a special handshake is performed.

First, the server sends a payload where the `op` is `HELLO` and the message field which is either `ALLOWED` or `DISALLOWED`.
If the server sends a `DISALLOWED` response, the server _immediately_ closes the websocket connection. This response is sent
when the server has reached its max client limit.

After a `ALLOWED` response from the server, the client must send a payload where the `op` is `HELLO`, and the `message` field
should contain the user's name in the form of a string.

After that, the server sends a payload to the user where the `op` is `ID_ASSIGN` and the message field contains a string
with a unique ID assigned to the client by the server.

The server then adds the client to the list of connected clients and further communication may now commence.

## Events

Below are the events that the server notifies the connected clients about and their respective payloads.

-   **New Member**  
     This event is occurs when a member joins the chat.

**Payload:**

```JSON
{
    op: "NEW_MEMBER",
    message: {
        client: {
            id: "Client ID"
            name: "User Name"
        }
    }
}
```

-   **New Message**
    This event occurs when a member sends a message.

**Payload:**

```JSON
{
    op: "NEW_MESSAGE",
    message: {
        client: {
            id: "Client ID",
            name: "User Name"
        },
        content: "Message content"
    }
}
```

## Methods

Below are the operations that clients are permitted to do.

-   **Create Message**

The below payload must be sent to the server, when the user wants to send a message.

**Payload:**

```JSON
{
    op: "CREATE_MESSAGE",
    message: "The message the user wants to send."
}
```
