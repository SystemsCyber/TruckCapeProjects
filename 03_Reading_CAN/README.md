# Notes for read_CAN.py

This solution should demonstrate the way raw controller area network data is read from SocketCAN.

See https://docs.python.org/3/library/struct.html for help with the interpretation string.

## Troubleshooting

### No such device
Symptom: 
You get this error when running ```python3 read_CAN.py```:

```
Traceback (most recent call last):
  File "read_CAN.py", line 20, in <module>
    sock.bind((interface,))
OSError: [Errno 19] No such device
```

Solution: You need to set the interface using the virtual can interface (vcan).

### No data is playing
Symptom: After running ```python3 read_CAN.py``` there is nothing happening in the terminal.

Solution: Use canplayer to send messages to the virtual CAN device. You'll need to download a CAN log to work with, like the one in this repository. For more logs, you can find information at https://www.engr.colostate.edu/~jdaily/J1939/candata.html.

Use the following command to run the canplayer in the background in an infinite loop:

```canplayer -l i -I candump_kw_drive.txt vcan0=can1&```



## Setting up vcan0
Follow instructions at https://www.kernel.org/doc/html/latest/networking/can.html#the-virtual-can-driver-vcan

To setup a virtual can interface, do the following:
```sudo ip link add type vcan```

Turn on the vcan interface:
```sudo ip link set vcan0 up```
