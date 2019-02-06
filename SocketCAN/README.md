# Regarding tcpCANClient.py and tcpCANServer.py

**tcpCANServer.py** must be first started

**tcpCANClient.py** then can be started indicating a CAN interface (can0 or can1)

CAN data will then flow from the *client* to *server* with output printing to the console of the server.
Using TCP means TCP packets are guarunteed to arrive and guarunteed to arrive in order.

**NOTE**: Currently only tested on localhost, or loopback address (127.0.0.1).
