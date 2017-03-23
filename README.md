# TruckCapeProjects
Projects teaching the basics of using the TruckDuck or Truck Cape on a Beagle Bone Black with Python.

The Linux image to run on the BeagleBone's eMMC can be downloaded, decompressed, imaged to an SD card. When the BeagleBone Black boots from the SD card, it will burn the eMMC to have the necessary contents to run the exercises in this repository. More specifically, the image will have the following:

1. ARM Linux Kernel 3. 
  
   ```uname -a```
  
   ```Linux truck-duck 3.8.13+ #3 SMP Fri Jul 1 14:46:43 CDT 2016 armv7l armv7l armv7l GNU/Linux```
  
2. J1939 Kernel Extension
3. can-utils
4. py-hv-drivers
5. Python 3.5.2
## Getting Started
### Windows Software
If this is your first time with a Heavy Truck Cape with BeagleBoneBlack, then you'll need some software on your computer to interface with it. This readme assumes you are using Windows. Linux and Mac have shell utilities built-in already. For Windows users, you'll need the following:
1. PuTTy
2. WinSCP 
3. BeagleBoneBlack Drivers

### Logging In
1. Plug in the a Mini USB cable between the BeagleBone and your computer
2. Open Putty. 
3. Specify the Host Name (or IP address) as 192.168.7.2
4. Press Open
5. Use the following credentials:

Default Credentials
U: ubuntu P: truckduck
Please change the password if this is connected to the Internet.

An ASCII art image of a duck should appear.

###

### Change the Baud Rate
To figure out the bitrate of the devices, issue the following command
```
ubuntu@truck-duck:~$ ip -details -statistics link show can1
```
which gives output like the following showing a bitrate of 250000 bps.
```
4: can1: <NOARP,UP,LOWER_UP,ECHO> mtu 16 qdisc pfifo_fast state UNKNOWN mode DEFAULT qlen 10
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
    j1939 on
```

Enter the following commmands to change the CAN bitrate to 666000 on the CAN0 channel.
CAN0 on SocketCAN is the CAN2 channel on the J1939 connector.
```
ubuntu@truck-duck:~$ sudo ip link set can0 down
[sudo] password for ubuntu: <Type in your password here>
ubuntu@truck-duck:~$ sudo ip link set can0 type can bitrate 666000
ubuntu@truck-duck:~$ sudo ip link set can0 up
ubuntu@truck-duck:~$ candump can0
```
The resulting terminal should display something like this if CAN0 is connected to a 666k CAN network.
```
ubuntu@truck-duck:~$ candump can0
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

## Installing the TruckDuck or TruckCape Distribution
The compressed sd card image is linked here: https://www.dropbox.com/s/j8maeqj8ru7p7ck/truck-duck-18sept2016.7z?dl=0

Reference Website: https://truckhacking.github.io/

## Converting the Truck Cape into a Datalogger
To make a logger, you can automatically start candump.

Add the following to the /etc/init/truckduck/truckduck.conf file at the end:

```#set up to automatically log on boot.
cd /home/ubuntu
candump -l any &
end script

```
The dated data files will be available in the home directory. You will have to log in to

## Challenge Assignments
### Log all data to an SD Card
Adapt the startup script to log all data from the J1939 (CAN1), CAN0, and Both J1708 channels to log to files on a large SD card installed in the BeagleBone card slot.

### Automatic RTC
Add the ability to set the time using the an I2C based Real Time Clock chip. Normal operation relies on a network connection to get time.

### Add LIN 
A LIN transceiver is on the Truck Cape. Enable this feature by using a built in serial port. 

### Support the Quadrature Input Knob
Add the ability for Linux to see the quadrature knob input for additional user input.

### Send and Receive CAN messages over UDP
Build a network bridge for CAN and Ethernet. 

### Build a can-utils website
Hose a website on the Beaglebone to interface with socket CAN

