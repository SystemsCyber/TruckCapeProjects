# Notes for read_CAN.py

This solution should demonstrate the way raw controller area network data is read from SocketCAN.

If you don't have a truck network to connect to, run this command to see network traffic virtually:
```canplayer -l i -I candump_kw_drive.txt vcan0=can1 &```

The challenge is to setup the correct struct format string to properly read the data from the SocketCAN interface. 
See https://docs.python.org/3/library/struct.html for help with the interpretation string.

Once your program is successful, the output may look something like this:

```debian@beaglebone:~/TruckCapeProjects/03_Reading_CAN/solution$ python3 read_CAN.py 
vcan0 18FEF200 [8] 8C 00 00 00 0D 06 0D FF
vcan0 18FEF500 [8] C4 FF FF 26 25 FF FF FF
vcan0 18FEC100 [8] 52 C5 3C 09 FF FF FF FF
vcan0 18FEE000 [8] FF FF FF FF 40 97 5E 00
vcan0 18FEBD00 [8] FF F0 00 00 FF FF FF FF
vcan0 18FEE400 [8] F0 FF FF FC F0 FF FF FF
vcan0 18FEF700 [8] FF FF FF FF 20 01 FF FF
vcan0 18FD7C00 [8] F8 F3 F3 FF FF FF E3 FF
vcan0 18EA3100 [3] E6 FE 00
vcan0 1CECFF0F [8] 20 13 00 03 FF E1 FE 00
vcan0 0CF00400 [8] 50 89 91 2C 15 00 F0 FF
vcan0 0CF00400 [8] 30 89 8F 2C 15 00 F0 FF
vcan0 08FE6E0B [8] E0 01 A0 01 A0 01 60 01
```

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

```canplayer -l i -I candump_kw_drive.txt vcan0=can1 &```



## Setting up vcan0
Follow instructions at https://www.kernel.org/doc/html/latest/networking/can.html#the-virtual-can-driver-vcan

To setup a virtual can interface, do the following:
```sudo ip link add type vcan```

Turn on the vcan interface:
```sudo ip link set vcan0 up```
