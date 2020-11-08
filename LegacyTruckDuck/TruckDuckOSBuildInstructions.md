# Original TruckDuck Build Instructions

More specifically, the image will have the following:

1. ARM Linux Kernel 3. 
  
   ```uname -a```
  
   ```Linux truck-duck 3.8.13+ #3 SMP Fri Jul 1 14:46:43 CDT 2016 armv7l armv7l armv7l GNU/Linux```
  
2. J1939 Kernel Extension
3. can-utils
4. py-hv-drivers
5. Python 3.5.2

Default Credentials
U: ubuntu P: truckduck
Please change the password if this is connected to the Internet.

An ASCII art image of a duck should appear.

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

