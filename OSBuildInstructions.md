# Installing the Linux Operating System.

These steps were taken to build the TruckCape recovery SD card. If you have a truck-cape from 2020, then these steps have already been done.

1. Download 

https://debian.beagleboard.org/images/bone-eMMC-flasher-debian-10.3-iot-armhf-2020-04-06-4gb.img.xz

1. Using a utility like 7zip, decompress the image.

1. Using Win32DiskImager, burn the Debian Linux distribution to a 4GB SD partition. This will be a flasher image that will overwrite the eMMC chip in the BeagleBone Black.

1. Insert the flasher image SD card into to the BeagleBone Black. Power on the BBB (i.e. plug in the USB) while depressing the SD boot button until the 4 user LEDs come on. After about 30 seconds, the flasher program will start as indicated by the user leds cycling in a back-and-forth pattern. The reflashing process could take 10-15 minutes, depending on the speed of the SD card. 

## Testing the System
Using an SSH client, like PuTTYy, and a USB to computer connection, connect to the Beagle Bone Black SSH using IP 192.168.7.2 on port 22.

The new login uses the following credentials:

U: debian

P: temppwd

The availability if this connection may take longer than you might like, but be patient, the board will finish booting and enumerate as a drive on your host computer. 


Connect a live Internet connection by the Ethernet cable into your Beagle Bone Black. Check to see if you have a valid IP address on `eth0`:

```
sudo ifconfig
```

### What Version do you have?
If you are having troubles, be sure you are using the same version that's documented here. When the kernel changes, the results may be different. 

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

Also, enable the universal overlay. This ensures the kernel has access to the hardware pin multiplexers. 

```
###Additional custom capes
uboot_overlay_addr4=/lib/firmware/cape-universal.dtbo
#uboot_overlay_addr5=/lib/firmware/<file5>.dtbo
#uboot_overlay_addr6=/lib/firmware/<file6>.dtbo
#uboot_overlay_addr7=/lib/firmware/<file7>.dtbo
###

```

Finally, enable uio_pruss kernel module for the Programmable Realtime Unit (PRU).
```
###PRUSS OPTIONS
###pru_rproc (4.14.x-ti kernel)
#uboot_overlay_pru=/lib/firmware/AM335X-PRU-RPROC-4-14-TI-00A0.dtbo
###pru_rproc (4.19.x-ti kernel)
#uboot_overlay_pru=/lib/firmware/AM335X-PRU-RPROC-4-19-TI-00A0.dtbo
###pru_uio (4.14.x-ti, 4.19.x-ti & mainline/bone kernel)
uboot_overlay_pru=/lib/firmware/AM335X-PRU-UIO-00A0.dtbo
###
```

Save and reboot: `sudo shutdown -r now`

Verify the uio_pruss kernel module is running:
```
lsmod | grep pru
```

### Configure the pins
Write the following commands to get the CAN hardware to access the pins upon boot. 
Create a file in the /etc directory:

```
sudo nano /etc/pin_config.sh
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
config-pin p8.34 pwm
config-pin p8.36 pwm
# GPIO
config-pin p9.12 gpio
config-pin p9.14 gpio

exit 0
```
Make the script executable:
```
sudo chmod +x /etc/pin_config.sh
```
However, these commands need to be run upon boot, so let's make a script to do this and add it to a boot sequence.

```
sudo nano /lib/systemd/system/pin_config.service
```
Add this to the file:
```
[Unit]
Description=Setup for BBB

[Service]
Type=simple
ExecStart=/bin/bash /etc/pin_config.sh

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
To confirm the pin_config.service was enabled, look for a symbolic link in `/etc/systemd/system`

```
debian@beaglebone:/etc/systemd/system$ ls -la
lrwxrwxrwx  1 root root   38 Sep 17 04:51 pin_config.service -> /lib/systemd/system/pin_config.service
```

Reboot and verify. `sudo shutdown -r now`

```
debian@beaglebone:~$ config-pin -q p9.24

Current mode for P9_24 is:     can

```

Verify the status of the pin_config.service was successful by looking for an output like this:

```
debian@beaglebone:~$ sudo systemctl status pin_config.service
● pin_config.service - Setup for BBB p
   Loaded: loaded (/etc/systemd/system/pin_config.service; enabled; vendor preset: enabled)
   Active: inactive (dead) since Tue 2020-09-08 23:52:06 UTC; 2min 18s ago
  Process: 856 ExecStart=/bin/bash /home/debian/pin_config.sh (code=exited, status=0/SUCCESS)
 Main PID: 856 (code=exited, status=0/SUCCESS)

Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P9_13 is:     uart
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P8_37 is:     uart
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P8_38 is:     uart
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P8_46 is:     pwm
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P8_45 is:     pwm
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P8_34 is:     pwm
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P8_36 is:     pwm
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P9_12 is:     gpio
Sep 21 14:06:18 beaglebone bash[2040]: Current mode for P9_14 is:     gpio
Sep 21 14:06:18 beaglebone systemd[1]: pin_config.service: Succeeded.
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
### Add virtual CAN drivers
The vcan interfaces are great ways to develop hardware without needing to troubleshoot physical CAN connections or have access to a truck.

Write a script to stand up some vcan devices. 
```
sudo nano /etc/network/vcan-start.sh
```
Enter these commands into the file:
```
#!/bin/sh -e
ip link add type vcan 
ip link set vcan0 up
ip link add dev vcan1 type vcan
ip link set vcan1 up
ip link add dev vcan2 type vcan
ip link set vcan2 up
exit 0
```

Make the script executable:
```
sudo chmod +x /etc/network/vcan-start.sh
```
This script should be run upon boot, so let's make a script to do this and add it to a boot sequence.

```
sudo nano /lib/systemd/system/vcan.service
```
Add this to the file:
```
[Unit]
Description=Turn on virtual CAN interfaces

[Service]
Type=simple
ExecStart=/bin/bash /etc/network/vcan-start.sh

[Install]
WantedBy=multi-user.target
```

Start the service

```
sudo systemctl start vcan.service
```

Verify the service

```
sudo systemctl status vcan.service
```
Enable the service at boot

```
sudo systemctl enable vcan.service
```
To confirm the pin_config.service was enabled, look for a symbolic link in `/etc/systemd/system`

```
ls -la /etc/systemd/system/multi-user.target.wants/
lrwxrwxrwx  1 root root   32 Nov  7 15:27 vcan.service -> /lib/systemd/system/vcan.service
```
should show a line
```
lrwxrwxrwx  1 root root   32 Nov  7 15:27 vcan.service -> /lib/systemd/system/vcan.service
```

Reboot and verify. `sudo shutdown -r now`
```
debian@beaglebone:~$ ifconfig


vcan0: flags=193<UP,RUNNING,NOARP>  mtu 72
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

vcan1: flags=193<UP,RUNNING,NOARP>  mtu 72
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

vcan2: flags=193<UP,RUNNING,NOARP>  mtu 72
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

Now there are 3 vcan channels ready for use. 

### Add Software Packages
Run these commands to get the latest versions.
```
sudo apt update
sudo apt upgrade
```

Run these commands to get dependencies for the Beagle Bone Black. 

Install Jupyter so we can run Jupyter notebooks on the Beagle Bone Black
```
sudo pip3 install jupyter
```

You can launch a jupyter notebook server from the Beagle Bone:
```
jupyter notebook --ip 192.168.7.2 --no-browser
```

These dependencies are needed for the Jupyter live plotting examples.
```
sudo apt install libjpeg-dev -y
sudo apt install zlib1g-dev -y
sudo apt install libfreetype6-dev -y
sudo apt install zip -y
sudo apt install libopenjp2-7 -y
```

Also, install the cryptography library:
```
sudo pip3 install cryptography
```
This should report  `Successfully installed cryptography-3.2.1`


### Truck Cape Projects
Clone the Git Repository
```
cd ~
git clone https://github.com/SystemsCyber/TruckCapeProjects.git
```

## J1708 drivers

Install PyPRUSS for both Python 2.7 and 3.7
```
git clone https://bitbucket.org/intelligentagent/pypruss.git  
cd pypruss
sudo python setup.py install
sudo python3 setup.py install
#export LD_LIBRARY_PATH=/usr/local/lib
```



### hv_networks
Install the hv_networks drivers. First, clone the repository, then install the packages.
```
git clone https://github.com/SystemsCyber/py-hv-networks.git
cd py-hv-networks
sudo python3 setup.py install
```

Copy the PRU files to the OS:
```
sudo cp -r bbonePRU /opt/
```

Create an init script to load the PRU drivers.
```
sudo nano /etc/load_j1708_drivers.sh 
```

Add the following contents:
```
#!/bin/sh -e
/opt/bbonePRU/ecm_driver.py
/opt/bbonePRU/non_ecm_driver.py
exit 0
```

Make the script executable:
```
sudo chmod +x /etc/load_j1708_drivers.sh 
```

Write a service to run this script on boot.
```
sudo nano /lib/systemd/system/ecm_driver.service
```
Add this to the file:
```
[Unit]
Description=Load Python Drivers to Load J1708 PRU code

[Service]
Type=simple
Restart=on-failure
RestartSec=3
ExecStart=/opt/bbonePRU/ecm_driver.py

[Install]
WantedBy=multi-user.target
```

It's important to include the restart features because the first time the script is run, it usually fails. The script gets invoked before all the PRU infrastructure is loaded. 

Test the service:
```
sudo systemctl start ecm_driver.service
```

Enable the service at boot:
```
sudo systemctl enable ecm_driver.service
```

Verify the ecm_drivers loaded:
```
sudo systemctl status ecm_driver.service
```

Repeat the a creation of the same service, but substitute `non_ecm_driver` for `ecm_driver`.


Reboot and see if things worked: `sudo shutdown -r now`

After rebooting, you can check the status of the service:
```
debian@beaglebone:~$ sudo systemctl status ecm_driver.service
● ecm_driver.service - Load Python Drivers to Load J1708 PRU code
   Loaded: loaded (/lib/systemd/system/ecm_driver.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2020-11-14 21:27:36 UTC; 36s ago
 Main PID: 2420 (python2.7)
    Tasks: 3 (limit: 1026)
   Memory: 2.7M
   CGroup: /system.slice/ecm_driver.service
           └─2420 python2.7 /opt/bbonePRU/ecm_driver.py

Nov 14 21:27:36 beaglebone systemd[1]: Started Load Python Drivers to Load J1708 PRU code.
Nov 14 21:27:37 beaglebone ecm_driver.py[2420]: AM33XX
Nov 14 21:27:37 beaglebone ecm_driver.py[2420]: File /opt/bbonePRU/text1.bin open passed
```

For more on the PRU: https://github.com/nesl/Cyclops-PRU


## Write a recovery SD card
With the heavy vehicle specific software installed, we can 
To duplicate the firmware image on the eMMC of the current Beagle Bone Black, do the following:
1. Remove the BBBlack from the truck cape. Power up with USB. 
1. Insert a blank SD card 4GB or bigger as soon as the user LEDs flash on boot. This timing seems to help ensure the SD card is recognized by the kernel. Plugging in the SD card later may not work. This is a physical hack to ensure the SD card can work.
1. Connect the Ethernet to a live Internet connection.
2. Login 
1. Update the scripts
```
cd /opt/scripts
git pull
```
2. Run the command 
```
sudo /opt/scripts/tools/eMMC/beaglebone-black-make-microSD-flasher-from-eMMC.sh 
```
3. Wait for the program to finish.
```
================================================================================
eMMC has been flashed: please wait for device to power down.
================================================================================
Calling shutdown
```
4. Eject the card. It is ready to use.

If the process fails, double check the SD card insertion and timing. 

## Future Work
This section documents some experimentation for upgrading the kernel and working with the J1939 SocketCAN extension. None of the examples or exercises use this section. In fact, none of the examples in this repository have been verified to work with this upgrade. 

### Upgrade the Linux Kernel Module for SocketCAN

First, we must upgrade the kernel version on the beaglebone. This step requires a connection between the beaglebone and the Internet.
From: https://elinux.org/Beagleboard:BeagleBoneBlack_Debian#Kernel_Upgrade


```
debian@beaglebone:~$ cd /opt/scripts/tools/
debian@beaglebone:~$ git pull
debian@beaglebone:~$ sudo ./update_kernel.sh --lts-5_4
debian@beaglebone:~$ sudo reboot
```

As of October 7, 2020, this updates to beaglebone kernel 5.4.66-ti-r18.

Next, we need the files for the can-j1939 kernel module. These may be found in the kernel_modules directory of the repository. If the TruckCapeProjects repository is not downloaded, you may download it with the following commands:
```
debian@beaglebone:~$ sudo git clone https://github.com/SystemsCyber/TruckCapeProjects.git
```
We also need to install the linux headers to build modules natively on the beaglebone.

```
debian@beaglebone:~$ sudo apt install linux-headers-`uname -r`

```

Once installed, navigate to the "j1939" directory and compile the kernel module using the "make" command.
```
debian@beaglebone:~$ cd ~/TruckCapeProjects/kernel_modules/j1939
```
Now we need to compile the kernel module.
```
debian@beaglebone:~/TruckCapeProjects/kernel_modules/j1939$ sudo make
```
After making the can-j1939 module, we need to put it into the correct folder.

```
debian@beaglebone:~/TruckCapeProjects/kernel_modules/j1939$ sudo mkdir /lib/modules/5.4.66-ti-r18/kernel/net/can/j1939
debian@beaglebone:~/TruckCapeProjects/kernel_modules/j1939$ sudo cp can-j1939.ko /lib/modules/5.4.66-ti-r18/kernel/net/can/j1939
```

```
debian@beaglebone:~$ sudo depmod
debian@beaglebone:~$ sudo modprobe can-j1939
```
The beaglebone kernel has now been upgraded and includes the j1939 module for SocketCAN.

As a final step, we need to install the correct Linux Header Files for local code compilation.

```
debian@beaglebone:~$ sudo apt-get install linux-headers-`uname -r`
debian@beaglebone:~$ sudo cp -r ~/TruckCapeProjects/header_files/include /usr/
```

The beaglebone kernel is now upgraded to 5.4.x and has the capability to both run and compile code which uses the can-j1939 kernel module.

### Socket-CAN and can-utils
Get the latest version of can-utils that supports J1939. Download the package using curl:

```
debian@beaglebone:~$ curl http://http.us.debian.org/debian/pool/main/c/can-utils/can-utils_2020.02.04-3_armhf.deb --output can-utils_2020.02.04-3_armhf.deb
```

Install the package using dpkg

```
debian@beaglebone:~$ sudo dpkg  -i can-utils_2020.02.04-3_armhf.deb
(Reading database ... 72570 files and directories currently installed.)
Preparing to unpack can-utils_2020.02.04-3_armhf.deb ...
Unpacking can-utils (2020.02.04-3) over (2018.02.0-1) ...
Setting up can-utils (2020.02.04-3) ...
Processing triggers for man-db (2.8.5-2) ...
```

https://github.com/linux-can/can-utils

This might be interesting: https://www.beyondlogic.org/example-c-socketcan-code/

### Python and CAN
https://www.thomas-wedemeyer.de/beaglebone-canbus-python.html

python-can


https://justkding.me/thoughts/python-sae-j1939-socket-support


## J1708 drivers
Follow the instructions at https://github.com/TruckHacking/plc4trucksduck 

Write a J1708 socket driver.

## Other Resources
https://www.element14.com/community/community/designcenter/single-board-computers/next-genbeaglebone/blog/2019/08/15/beaglebone-black-bbb-io-gpio-spi-and-i2c-library-for-c-2019-edition
