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



## J1708 drivers
Follow the instructions at https://github.com/TruckHacking/plc4trucksduck 
