# Installing the Linux Operating System.
1. Download 

https://debian.beagleboard.org/images/bone-eMMC-flasher-debian-10.3-iot-armhf-2020-04-06-4gb.img.xz

1. Using a utility like 7zip, decompress the image.

1. Using Win32DiskImager, burn the Debian Linux distribution to a 4GB SD partition. This will be a flasher image that will overwrite the eMMC chip in the BeagleBone Black.

1. Insert the flasher image SD card into to the BeagleBone Black. Power on the BBB (i.e. plug in the USB) while depressing the SD boot button until the 4 user LEDs come on. After about 30 seconds, the flasher program will start as indicated by the user leds cycling in a back-and-forth pattern. The reflashing process could take 10-15 minutes, depending on the speed of the SD card. 

## Testing the System
Using an SSH client, like Putty, and a USB to computer connection, connect to the Beagle Bone Black SSH using IP 192.168.7.2 on port 22.

The new login uses the following credentials:

U: debian

P: temppwd

The availability to boot is longer than you might like, but be patient, the board will finish booting and enumerate as a drive on your host computer. 


Connect an active Ethernet cable into your BeagleBone. Check to see if you have a valid IP address on `eth0`:

```
sudo ifconfig
```

### What Version do you have?
Enter the following command `cat /etc/dogtag`:

```
debian@beaglebone:~$ cat /etc/dogtag
BeagleBoard.org Debian Buster IoT Image 2020-04-06
```

Check the kernel version:

```
debian@beaglebone:~$ uname -a
Linux beaglebone 4.19.94-ti-r42 #1buster SMP PREEMPT Tue Mar 31 19:38:29 UTC 2020 armv7l GNU/Linux
```


## Pin Multiplexing Setup for CAN and Others

References:

https://www.beyondlogic.org/adding-can-to-the-beaglebone-black/

https://www.bacpeters.com/2020/01/25/configuring-the-beaglebone-black-gpio-pins-permanently/

### Disable Unused Hardware
Edit the uEnv.txt file and uncomment the some disable commands. This opens the pins up for accessing other functions.

```
sudo nano /boot/uEnv.txt
```
Uncommment the disable_uboot_overlay as follows:
```
#dtb_overlay=/lib/firmware/<file8>.dtbo
###
###Disable auto loading of virtual capes (emmc/video/wireless/adc)
#disable_uboot_overlay_emmc=1
disable_uboot_overlay_video=1
disable_uboot_overlay_audio=1
disable_uboot_overlay_wireless=1
disable_uboot_overlay_adc=1
###
```
Be sure to keep the emmc line commented, since that's the root file system.

Save and reboot: `sudo shutdown -r now`


### Configure the pins
Write the following commands to get the CAN hardware to access the pins upon boot. 
Create a file in the home directory:

```
nano /home/debian/pin_config.sh
```
Write the following into the directory:
```
#!/bin/sh -e
# DCAN1
config-pin p9.24 can
config-pin p9.26 can 
# DCAN0
config-pin p9.19 can
config-pin p9.20 can
#ttyO2:
config-pin p9.21 uart
config-pin p9.22 uart
#ttyO4:
config-pin p9.11 uart
config-pin p9.13 uart
#ttyO5:
config-pin p8.37 uart
config-pin p8.38 uart
# PWMs
config-pin p8.46 pwm
config-pin p8.45 pwm
config-pin p8.44 pwm
config-pin p8.43 pwm
# GPIO
config-pin p8.36 gpio
config-pin p9.12 gpio
config-pin p9.14 gpio

exit 0
```
Make the script executable:
```
sudo chmod +x /home/debian/pin_config.sh
```
However, these commands need to be run upon boot, so let's make a script to do this and add it to a boot sequence.

```
sudo nano /etc/systemd/system/pin_config.service
```
Add this to the file:
```
[Unit]
Description=Setup for BBB

[Service]
Type=simple
ExecStart=/bin/bash /home/debian/pin_config.sh

[Install]
WantedBy=multi-user.target
```

Start the service

```
sudo systemctl start pin_config.service
```

Verify the service

```
sudo systemctl status pin_config.service
```
Enable the service at boot

```
sudo systemctl enable pin_config.service
```
Reboot and verify:

```
config-pin -q p9.24
```

Verify the status of the pin_config.service was successful by looking for an output like this:

```
debian@beaglebone:~$ sudo systemctl status pin_config.service
● pin_config.service - Setup for BBB p
   Loaded: loaded (/etc/systemd/system/pin_config.service; enabled; vendor preset: enabled)
   Active: inactive (dead) since Tue 2020-09-08 23:52:06 UTC; 2min 18s ago
  Process: 856 ExecStart=/bin/bash /home/debian/pin_config.sh (code=exited, status=0/SUCCESS)
 Main PID: 856 (code=exited, status=0/SUCCESS)

Sep 08 23:52:05 beaglebone bash[856]: Current mode for P8_37 is:     uart
Sep 08 23:52:05 beaglebone bash[856]: Current mode for P8_38 is:     uart
Sep 08 23:52:06 beaglebone bash[856]: Current mode for P8_46 is:     pwm
Sep 08 23:52:06 beaglebone bash[856]: Current mode for P8_45 is:     pwm
Sep 08 23:52:06 beaglebone bash[856]: Current mode for P8_44 is:     pwm
Sep 08 23:52:06 beaglebone bash[856]: Current mode for P8_43 is:     pwm
Sep 08 23:52:06 beaglebone bash[856]: Current mode for P8_36 is:     gpio
Sep 08 23:52:06 beaglebone bash[856]: Current mode for P9_12 is:     gpio
Sep 08 23:52:06 beaglebone bash[856]: Current mode for P9_14 is:     gpio
Sep 08 23:52:06 beaglebone systemd[1]: pin_config.service: Succeeded.
```
If this doesn't work, be sure to disable the overlays in the uEnv.txt file.


### Start the network interfaces
Edit your `/etc/network/interfaces` file.

```
sudo nano /etc/network/interfaces
```

Add the following lines:

```
allow-hotplug can1
 iface can1 can static
    bitrate 250000

allow-hotplug can0
 iface can0 can static
    bitrate 250000
```
Reboot: `sudo shutdown -r now`

Upon restart, the CAN interfaces should be mounted.

```
debian@beaglebone:~$ sudo ifconfig
[sudo] password for debian:
can0: flags=193<UP,RUNNING,NOARP>  mtu 16
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
        RX packets 19375  bytes 155000 (151.3 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 42

can1: flags=193<UP,RUNNING,NOARP>  mtu 16
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
        RX packets 50893  bytes 407139 (397.5 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 43

eth0: flags=-28669<UP,BROADCAST,MULTICAST,DYNAMIC>  mtu 1500
        ether ec:24:b8:72:7d:ef  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 55

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 400  bytes 27920 (27.2 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 400  bytes 27920 (27.2 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

usb0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.7.2  netmask 255.255.255.0  broadcast 192.168.7.255
        inet6 fe80::ee24:b8ff:fe72:7df1  prefixlen 64  scopeid 0x20<link>
        ether ec:24:b8:72:7d:f1  txqueuelen 1000  (Ethernet)
        RX packets 1895  bytes 136356 (133.1 KiB)
        RX errors 0  dropped 4  overruns 0  frame 0
        TX packets 2105  bytes 472901 (461.8 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

usb1: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 192.168.6.2  netmask 255.255.255.0  broadcast 192.168.6.255
        ether ec:24:b8:72:7d:f5  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
If there is a live CAN bus connected, try `candump any` and confirm message traffic.

```
debian@beaglebone:~$ candump any
  can0  0CFEF100   [8]  FB FF FE AA AA 00 1F FF
  can1  08FE6E0B   [8]  FF FE FF FE FF FE FF FE
  can1  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can0  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can1  18F00E00   [8]  A0 0F FE 71 FF FF FF FF
  can0  18E0FF00   [8]  00 FF FF FF FF FA FF FF
  can1  18FEF200   [8]  00 00 FF FE BF 05 FE FF
  can1  18FEDF00   [8]  86 FF FF FF 7D FF FE 00
  can1  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can0  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can0  18F0000F   [8]  20 7D 7D F3 00 7D FE 63
  can1  10FDA300   [8]  FF FF FA FF FF FF FF FF
  can1  18FEE000   [8]  FF FF FF FF 0F 14 0A 00
  can1  18FD0900   [8]  FF FF FF FF 0C 78 B6 01
  can1  08FE6E0B   [8]  FF FE FF FE FF FE FF FE
  can1  1CEBFF00   [8]  0C 01 7F 02 09 01 84 06
  can0  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can1  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can0  18FEF200   [8]  00 00 FF FE BF 05 FE FF
  can1  18FF4500   [8]  78 2A FA 00 FF 00 00 AC
  can1  18FEDF00   [8]  86 FF FF FF 7D FF FE 00
  can1  1CFE9200   [8]  FF 80 97 FF FF FF FF FF
  can1  18F0010B   [8]  CC FF F0 FF FF 5C FF FF
  can1  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can0  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
  can1  0CF00300   [8]  FA FE 00 FF FF 0C 00 FF
  can0  18FEE000   [8]  FF FF FF FF 0F 14 0A 00
  can1  18FEEF00   [8]  FE FF FF FE FF FF FF 00
  can1  18FF4800   [8]  00 00 F3 FF 00 00 00 00
  can1  18FEE0CA   [8]  FF FF FF FF FF FF FF FF
  can1  18FEBF0B   [8]  FF FE FE FE FE FE FF FF
  can1  08FE6E0B   [8]  FF FE FF FE FF FE FF FE
  can1  0CF00400   [8]  00 7D 7D 00 00 00 F0 7D
```

### Socket-CAN and CAN-UTILS
https://github.com/linux-can/can-utils

This now has J1939.



This might be interesting: https://www.beyondlogic.org/example-c-socketcan-code/

### Python and CAN
https://www.thomas-wedemeyer.de/beaglebone-canbus-python.html

python-can


## J1708 drivers
Follow the instructions at https://github.com/TruckHacking/plc4trucksduck 

Write a J1708 socket driver.

## Other Resources
https://www.element14.com/community/community/designcenter/single-board-computers/next-genbeaglebone/blog/2019/08/15/beaglebone-black-bbb-io-gpio-spi-and-i2c-library-for-c-2019-edition
