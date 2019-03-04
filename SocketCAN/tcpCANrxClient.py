#!/usr/bin/python3

import time
import socket
import sys
import select

# Open a socket and bind to it from SocketCAN
canSock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
canSock.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_ERR_FILTER, socket.CAN_ERR_MASK) #allows socket to receive error frames
# The interface can be seen from the command prompt (ifconfig)
# The can channel must be configured using the ip link commands
interface = input("Pick an interface! ( can1 | can0 ): ")
if interface.strip('\n') != 'can0': interface = 'can1' #forces can1 if not can0

print('---------------------------------------------------------------------')
print("Opening CAN Socket on {}.".format(interface))
# Bind to the interface
try:
    canSock.bind((interface,))
except OSError:
    print("Could not bind to interface '%s'\n" % interface)
    sys.exit()

#setup tcp client for CAN data transfer
SERVER_IP = "127.0.0.1" #insert IP address of server here
SERVER_PORT = 2319

print("Streaming CAN data to IP Address {} on Port {}.", SERVER_IP, SERVER_PORT)
print('---------------------------------------------------------------------')

tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcpSocket.connect((SERVER_IP, SERVER_PORT))
except OSError:
    print("Could not connect TCP Socket. Make sure SERVER_IP is correct.")
    sys.exit()

#initilization of looping parameters TCP packet/Ethernet frame refering to same message
numCANFrames = 0 #used to store number of CAN frames in tcp packet
ethData = b'' #used to store payload of ethernet frame
MIN_ETH_PAYLOAD = 46 #min size of eth packet
TIMEOUT = 5 #amount of time in seconds allowed to not receive a CAN Frame
MAX_CAN_PER_TCP = 89 #the maxiumum number of allowed can frames in each tcp packet
###  NOTE: The client will shutdown if the timeout is reached, otherwise it will keep sending 
###        only the maximum amount of CAN frames in each tcp packet. MAX_CAN_PER_TCP maxes out at
###        89 CAN frames since the number of bytes of the payload in the packet is 1424, and the
###        max size of an ethernet payload is 1500 bytes and each CAN frame takes 16 bytes.
###        IP header takes 20 bytes and TCP header with options => 40 bytes to be safe. Total bytes = 1500
startTime = time.time() #start time of data transfer
currentTime = time.time() #current time in seconds
lastCANReadTime = time.time() #stores the time of the last read message starting at current time

SEC_TO_MICROS = 1000000 #converts seconds to micros by multiplication

#loop for sending tcp packets

print(currentTime, " ", lastCANReadTime)

while currentTime - lastCANReadTime < TIMEOUT: #loops until the timeout of CAN messages occurs
    currentTime = time.time()
    while select.select([canSock],[],[],1)[0]: #while a CAN frame is on the interface
        canFrame = canSock.recv(16) #just append the raw bytes from the socket, no need to unpack on this end
        numCANFrames += 1 #increment num of CAN frame counter
        lastCANReadTime = time.time() #resets timer to indicate message just was read
        if int((lastCANReadTime - startTime)*SEC_TO_MICROS) >= 0xFFFFFF: startTime = lastCANReadTime #resets start time to rollover timestamp
        microTimer = (int((lastCANReadTime - startTime)*SEC_TO_MICROS)).to_bytes(3, byteorder='little')
        ethData += canFrame[:5] + microTimer + canFrame[8:] #replaces padded bytes with microsecond timer
        if (numCANFrames >= MAX_CAN_PER_TCP):
            ethData = bytes([numCANFrames]) + ethData #concatenates size as first byte of frame
            print("Sending full frame")
            tcpSocket.send(ethData)
            ethData = b''
            numCANFrames = 0
while len(ethData) < MIN_ETH_PAYLOAD: #more than enough padding
    ethData += b'\x00' #pads frame to min size of ethernet frame
print("Sending padded frame [FINAL]")
tcpSocket.send(ethData)
tcpSocket.close()