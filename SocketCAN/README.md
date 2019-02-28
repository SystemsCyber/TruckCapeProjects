# Overview

There are 2 functionalities regarding the scripts
    - tcpCANrxServer.py
    - tcpCANrxClient.py
    - tcpCANClient.py
    - tcpCANServer.py
    - rxServers.py
1) tcpCANrxServer.py and tcpCANrxClient.py are used to establish a simple stream of CAN data from a node connected to a vehicle network to a remote server and to log the messages on the server.

2) tcpCANServer.py, tcpCANClient.py, and rxServers.py extend **1)** by adding a control server to turn on/off data transfer read from a CAN interface and add more capabilities.
    - Transmitting CAN frames embedded in TCP packets
    - Changing bitrate of CAN interface
    - Turning on/off or resetting CAN interface
    - Viewing estimated busload of a given interface
    - Obtaining a count of CAN messages to transmit and received CAN messages transferred over a TCP connection

Directions on how to set up the files and which machines host each file are explained within each of the Setting Up sections.

## Regarding tcpCANrxClient.py and tcpCANrxServer.py

**These scripts are used to transfer CAN data from a vehicle network (client) to another machine (server) and log on the server.**

**tcpCANrxServer.py** must be first started.

**tcpCANrxClient.py** then can be started indicating a CAN interface (can0 or can1).

CAN data will then flow from the *client* to *server* with output printing to the console of the server.

The server will log the CAN frames to a unique file name. The directory can be specified with the appropriate variable DIRECTORY_NAME in **tcpCANrxServer.py**.

Using TCP means TCP packets are guaranteed to arrive and guaranteed to arrive in order.

### Setting Up

1. Install all dependencies and put tcpCANrxServer.py on the desired machine to receive CAN frames.
2. Install all dependencies and put tcpCANrxClient.py on the node connected to the vehicle network.
3. Execute tcpCANrxServer.py on the server machine.
4. Set the variable SERVER_IP in tcpCANrxClient.py to the displayed IP address from the tcpCANrxServer.py script.
5. Set the variable DIRECTORY_NAME in tcpCANrxClient.py to appropriate logging directory. (Default is where tcpCANrxServer.py is stored.)
6. Execute tcpCANrxClient.py

## Regarding tcpCANClient.py, tcpCANServer.py, and rxServers.py

**These scripts are used to establish a control server that accepts requests to transmit CAN data, receive CAN data, and change CAN interface settings on different interfaces.**

**tcpCANServer.py** should be hosted on the node connected to the vehicle interface.
- Running on a BeagleBone might require editing the file /etc/hosts to an appropriate IP address for the hostname.

**tcpCANClient.py** should be executed on the machine where CAN data is desired.

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
    - setbitrate (0x07) Changes the designated CAN Interface to the specified bitrate. Changing the bitrate is achieved using this command alone instead of combining it with down and up.
    - busload (0x08) Returns the estimated busload percentage of the designated CAN Interface by using can-utils.
    - rxmsgs (0x09) Returns the number of messages received since the port has been open. Will return 0 if no messages received or rxport is down.
    - txmsgs (0x10) Returns the number of messages transferred since the port has been open. Will return 0 if no messages transferred or txport is down.
* Parameter(s): Variable number of bytes storing parameters associated with command. Default is 0 bytes unless specified here.
    - setbitrate: 3 bytes storing the desired bitrate in hexadecimal big-endian format.

Examples:
- Turning on stream to transfer received vehicle messages on can0: b'\x00\x00' `python3 tcpCANClient.py can0 rxon`
- Reseting can1 Interface: b'\x01\x06' `python3 tcpCANClient.py can1 reset`
- Setting all Interfaces to 250,000 bitrate: b'\xFF\x07\x03\xD0\x90' `python3 tcpCANClient.py any setbitrate 250000`

* An additional command exists with the form `python3 tcpCANClient.py <interface> cangen` where interface is can0 or can1.
	- This command loops TCP packets containing CAN frames to the txservers which are transmitted on the vehicle network.
	- txon must be used first
* For the interface setting commands: down, up, reset, setbitrate
    - Authentication is necessary for first command.
    - Currently, the password authentication process is built into the server.
    - The client does not accept or transfer the password. It would need to be encrypted if it did.

### Setting Up

1. Install all dependencies and put tcpCANServer.py on the node connected to the vehicle network.
2. Install all dependencies and put tcpCANClient.py and rxServers.py on the desired machine to receive CAN frames.
3. Set the variable DIRECTORY_NAME in rxServers.py to appropriate logging directory. (Default is where rxServers.py is stored.)
4. Set the variable SERVER_IP in tcpCANClient.py to the displayed IP address from executing the tcpCANServer.py script.
5. Execute rxServers.py. This script must be restarted after the messages have stopped if another logging event is desired.
6. Execute tcpCANServer.py.
7. Execute tcpCANClient.py with command line arguments as documented when running `python3 tcpCANClient.py` for the desired command.

**NOTE:** If IP addresses are not properly displayed, OS configuration files may not be accurate and need to be edited.

When turning off rx streaming channels, the process will terminate *after* a timeout or *after* the latest TCP packet is filled and sent.
So, terminating any CAN interface with the command `python3 tcpCANClient.py any rxoff` will end one interface after the other in the order specified in the intfOrder list within tcpCANServer.py.
Therefore, it might take time to close all communication channels if the interfaces have a low percentage busload.
This design is to ensure that the last messages are not dropped. This means, rxServers.py must not be closed. It will close itself upon last packet.

The tcpCANClient.py is used to issue commands to the tcpCANServer.py. rxServers.py are the servers on the destination machine that receives the vehicle messages from the TCP connection.

Transferring CAN messages for RX and TX is done in the following format

    ------------------------------------------------------------------
    | Number of CAN Frames | CAN Frame | CAN Frame | ... | CAN Frame |
    ------------------------------------------------------------------

* Number of CAN Frames: One byte indicating number of CAN Frames that follow (0 to 89)
* CAN Frame: 16 bytes similar to socketCAN format
   
    ------------------------------------
    | Identifier | DLC | Micros | Data |
    ------------------------------------
- Identifier: 4 bytes for the ID of the CAN frame
- Data Length Code (DLC): 1 byte for the number of bytes in Data (0 to 8)
- Micros: 3 bytes for an elapsed microseconds timer from start of transfer (Doesn't apply to TX)
- Data: 0 to 8 bytes payload. (Will always have 8 bytes because of padding. DLC defines which bytes are actual data.)

## Problems and Solutions

* IP Address is incorrect on server files?
    - edit /etc/hosts file to appropriate IP address (refers to specific implementation of ubuntu)
* No buffer space available on tx servers?
    - run command `sudo ifconfig can1 txqueuelen 1000` for each interface, where can1 can be replaced with the specific CAN interface name (can0/can1/etc.)
    - issues can also come from needing to buffer due to low priority/high busload.
* Messages not being transmitted on txservers?
    - Additional txon commands are needed if the connection is severed.
    - For example, if TCPCAN messages are sent to a tx server in a loop and CTRL+C is used on the looped TCP client, the txon command will need to be used again before trying to send more messages.