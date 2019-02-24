# Regarding tcpCANrxClient.py and tcpCANrxServer.py

**These scripts are used to transfer CAN data from a vehicle network (client) to another machine (server) and log on the server.**

**tcpCANrxServer.py** must be first started

**tcpCANrxClient.py** then can be started indicating a CAN interface (can0 or can1)

CAN data will then flow from the *client* to *server* with output printing to the console of the server.

The server will log the CAN frames to a unique file name. The directory can be specified with the appropriate variable DIRECTORY_NAME in **tcpCANrxServer.py**.

Using TCP means TCP packets are guarunteed to arrive and guarunteed to arrive in order.

## Setting Up

1. Install all dependencies and put tcpCANrxServer.py on the desired machine to receive CAN frames.
2. Install all dependencies and put tcpCANrxClient.py on the node connected to the vehicle network.
3. Execute tcpCANrxServer.py on the server machine.
4. Set the variable SERVER_IP in tcpCANrxClient.py to the displayed IP address from the tcpCANrxServer.py script.
5. Set the variable DIRECTORY_NAME in tcpCANrxClient.py to appropriate logging directory. (Default is where tcpCANrxServer.py is stored.)
6. Execute tcpCANrxClient.py

# Regarding tcpCANClient.py and tcpCANServer.py

**These scripts are used to establish a control server that accepts request to transfer and receive CAN data on different interface.**

**tcpCANServer.py** should be hosted on the node connect to the vehicle interface.
- Running on a BeagleBone might require editing the file /etc/hosts to an appropriate IP address for the hostname.

**tcpCANClient.py** should be executed on the machine where CAN related commands are required.

The server accepts commands from TCP packets in the following format.

    ------------------------------------------
    | CAN Interface | Command | Parameter(s) |
    ------------------------------------------

* CAN Interface: One byte indicating which interface the command applies. (0x00 = can0, 0x01 = can1, 0xFF = any/all)
* Command: One byte indicating the command for the given interface.
    - rxon  (0x00) Turns on the associated port for streaming CAN messages to the IP Address of the machine initiating the command.
    - rxoff (0x01) Turns off the associated port for streaming CAN messages.
    - txon (0x02) Turns on the associated port for sending CAN messages from the IP Address of the machine initiating the command.
    - txoff (0x03) Turns off the associated port for sending CAN messages.
    - down (0x04) Turns off the designated CAN Interface.
    - up (0x05) Turns on the designated CAN Interface.
    - reset (0x06) Resets the designated CAN Interface. Equivalent to a down command then an up command.
    - setbitrate (0x07) Changes the designated CAN Interface to the specified bitrate.
    - busload (0x08) Returns the estimated busload percentage of the designated CAN Interface by using can-utils.
    - rxmsgs (0x09) Returns the number of messages received since the port has been open. Will return 0 if no messages receieved or rxport is down.
    - txmsgs (0x10) Returns the number of messages transferred since the port has been open. Will return 0 if no messages transferred or txport is down.
* Parameter(s): Variable number of bytes storing parameters associated with command. Default is 0 bytes unless specified here.
    - setbitrate: 3 bytes storing the desired bitrate in hexadecimal big-endian format.

Examples:
- Turning on stream to transfer received vehicle messages on can0: b'\x00\x00'
- Reseting can1 Interface: b'\x01\x06'
- Setting all Interfaces to 250,000 bitrate: b'\xFF\x07\x03\xD0\x90'

