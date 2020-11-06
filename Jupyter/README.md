# Jupyter Notebooks with CAN and J1939
The Jupyter Notebooks provide an alternative interface with working with the BeagleBone using Python. 

The approach is to setup a server on the BeagleBone and interface using a local computer with a browser. This approach uses a local network connection that may not be secure. Please do not use this with publically facing networks. The USB connection is ideal.

## Setup
The process takes advantage of the `canplayer` functionality of the can-utils for SocketCAN. To use this, we need to add virtual CAN interfaces.
    
  1. Add the vcan networking kernel module:
 ```sudo ip link add type vcan```

  2. Enable a few vcan interfaces and turn them on:
```
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up
sudo ip link add dev vcan1 type vcan
sudo ip link set vcan1 up
sudo ip link add dev vcan2 type vcan
sudo ip link set vcan2 up
sudo ip link add dev vcan3 type vcan
sudo ip link set vcan3 up
```
  3. Obtain a candump file. For example, you can get one from a public source:
```    
wget https://www.engr.colostate.edu/~jdaily/J1939/files/candump_kw_drive.zip
```
  4. Unzip the candump file:
```
unzip candump_kw_drive.zip
```
  5. Install can-utils to get canplayer (this is probably already done):
```
sudo apt install can-utils
```
  6. Install screen to detatch terminals
  ```
sudo apt install screen
  ```
  6. Set canplayer to play an infinite loop of the CAN log in the background. Once this is going, you can logout of the machine and the vcan0 interface will still have data.

```
screen
canplayer -l i -I candump_kw_drive.txt vcan0=can1 &
exit
```
8. Test the CAN Traffic by looking for vehicle speed messages from the Engine Control Module. 
```
candump vcan0 | grep FEF100
```
  7. Install Jupyter notebooks for everyone:
```
sudo pip3 install jupyter
```
  8. Start the jupyter notebook for the server using the server's ip address or url. This is for the BeagleBone connected by USB.
```
jupyter notebook --ip 192.168.7.2 --no-browser
```
 9. Copy and paste the url with the token into your browser window. Selecting text in PuTTy automatically copies it to the clipboard. For example:
```
http://192.168.7.2:8888/?token=728d33d4fe46550a8e6b77c26aecf0954d44506887132fd0
```

## Exercises
With the canplayer running and vcan interfaces up, work through the different jupyter notebooks in sequence.