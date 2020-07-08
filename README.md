# Message-Relay Server

A simple chat server made using the Websockets protocol.

## Usage

This is a chat _server_, that is it handles the connections from incoming clients and follows a strict protocol,
in sending and receiving messages.

You have to implement your own client or use the standard browser based JS client, which you can find [here](https://github.com/NightShade256/mr-client).
You can read about the server protocol [here](https://github.com/NightShade256/mr-server/blob/master/PROTOCOL.md), if you want to implement your own client.

To start the server,

1. First, install the dependencies,  
   `pip install -U -r requirements.txt`

2. Second, run the server as,  
   `python launcher.py <port> <max_clients>`

where, `port` is the port on which the server must listen for connections,  
and `max_clients` being the number of clients that can concurrently connect to the server.

## Note

This is just a project I made during my free time for learning purpose.

## License

This project is licensed under the MIT License.

## Support

If you stumble across this repository somehow and want some help regarding this, please feel free to contact me
on Discord.  
Username: `__NightShade256__`
