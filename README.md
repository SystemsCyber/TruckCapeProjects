# TruckCapeProjects
Projects teaching the basics of using the TruckDuck or Truck Cape on a Beagle Bone Black with Python.

## Getting Started
Login to your beaglebone and run the following command to copy this repository into your directory:

```git clone https://github.com/SystemsCyber/TruckCapeProjects.git```

Once this is copied in, you can update the repository by changing directory into the repostory and running ```git pull```

## Hardware
See the docs directory for details. You can buy the board directly from OSHPark and source the parts from Digikey or Mouser. 

## Linux
The Linux image to run on the BeagleBone's eMMC can be downloaded, decompressed, imaged to an SD card. When the BeagleBone Black boots from the SD card, it will burn the eMMC to have the necessary contents to run the exercises in this repository. 

Follow the guidance in [](OSBuildInstructions.md)

## Getting Started
### Windows Software
If this is your first time with a Heavy Truck Cape with BeagleBoneBlack, then you'll need some software on your computer to interface with it. This readme assumes you are using Windows. Linux and Mac have shell utilities built-in already. For Windows users, you'll need the following:
1. PuTTy
2. WinSCP 

### Logging In
1. Plug in the a Mini USB cable between the BeagleBone and your computer
2. Open PuTTy. 
3. Specify the Host Name (or IP address) as 192.168.7.2
4. Press Open
5. Use the following credentials:

Default Credentials
U: debian P: temppwd
Please change the password if this is connected to the Internet.


### Logging Out or Shutting Down
The system may shut down if the +12V feed is removed, even if the USB or 5V power jack is connected. Be sure to shut down the Linux system before unplugging the device. 

### Change the Baud Rate
To figure out the bitrate of the devices, issue the following command
```
ip -details -statistics link show can1
```
which gives output like the following showing a bitrate of 250000 bps.
```
can1: <NOARP,UP,LOWER_UP,ECHO> mtu 16 qdisc pfifo_fast state UNKNOWN mode DEFAULT qlen 10
    link/can
    can state ERROR-PASSIVE (berr-counter tx 0 rx 127) restart-ms 0
    bitrate 250000 sample-point 0.875
    tq 250 prop-seg 6 phase-seg1 7 phase-seg2 2 sjw 1
    c_can: tseg1 2..16 tseg2 1..8 sjw 1..4 brp 1..1024 brp-inc 1
    clock 24000000
    re-started bus-errors arbit-lost error-warn error-pass bus-off
    0          0          0          123        25203      0
    RX: bytes  packets  errors  dropped overrun mcast
    2611059    336058   0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    0          0        0       0       0       0
```

Enter the following commmands to change the CAN bitrate to 666000 on the CAN0 channel.
CAN0 on SocketCAN is the CAN2 channel on the J1939 connector.
```
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 666000
sudo ip link set can0 up
```
The resulting terminal should display something like this if CAN0 is connected to a 666k CAN network.
```
candump can0
  can0  10EBFF3D   [8]  01 00 00 00 00 00 00 00
  can0  10EBFF3D   [8]  01 00 00 00 00 00 00 00
  can0  10EBFF3D   [8]  01 00 00 00 00 00 00 00
  can0  08FE6E0B   [8]  FF FF FF FF FF FF FF FF
  can0  14FEAE17   [8]  FF FF FF FF FF FF FF FF
  can0  08FF0400   [8]  01 00 00 00 A8 61 4D 12
  can0  08FF0400   [8]  01 00 00 00 A8 61 6D 76
  can0  10EBFF3D   [8]  01 00 00 00 00 00 00 00
  can0  08FF0400   [8]  01 00 00 00 A8 61 4D 12
```

A similar strategy will be used for CAN1 and other bit rates.

## Challenge Ideas
### Log all data to an SD Card
Adapt the startup script to log all data from the J1939 (CAN1), CAN0, and Both J1708 channels to log to files on a large SD card installed in the BeagleBone card slot.

### Automatic RTC
Add the ability to set the time using the an I2C based Real Time Clock chip. Normal operation relies on a network connection to get time.

### Add LIN 
A LIN transceiver is on some versions of the Truck Cape. Enable this feature by using a built in serial port. 

### Send and Receive CAN messages over UDP
Build a network bridge for CAN and Ethernet. 

### Build a can-utils website
Host a website on the Beaglebone to interface with SocketCAN

