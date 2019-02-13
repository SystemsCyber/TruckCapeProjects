# Regarding tcpCANClient.py and tcpCANServer.py

**tcpCANServer.py** must be first started

**tcpCANClient.py** then can be started indicating a CAN interface (can0 or can1)

CAN data will then flow from the *client* to *server* with output printing to the console of the server.

The server will log the CAN frames to a file named canlog.txt unless otherwise specified.

Using TCP means TCP packets are guarunteed to arrive and guarunteed to arrive in order.

## Setting Up

1. Install all dependencies and put tcpCANServer.py on the desired machine to receive CAN frames.
2. Install all dependencies and put tcpCANClient.py on the node connected to the vehicle network.
3. Execute tcpCANServer.py on the server machine.
4. Set the variable SERVER_IP in tcpCANClient.py to the displayed IP address from the tcpCANServer.py script.
5. Set the variable DIRECTORY_NAME in tcpCANClient.py to appropriate logging directory. (Default is where tcpCANServer.py is stored.)
6. Execute tcpCANClient.py

