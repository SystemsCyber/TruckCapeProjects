#!/usr/bin/python3

import socket
import sys
import time

def printHelp():
    print("\n\nUsage: python3 tcpCANClient.py <CAN interface> <CAN command> [parameters]\n\n")
    print("NOTE: No parameters must be given for commands with parameter = NONE.\n\n")
    print("CAN Interfaces: can0")
    print("                can1")
    print("                any (all CAN interfaces listed above, limits on commands may apply))\n")
    print("CAN Commands:   rxon        (turns TCP rx messages on)             [parameter = NONE]")
    print("                rxoff       (turns TCP rx messages off)            [parameter = NONE]")
    print("                txon        (turns TCP tx messages on)             [parameter = NONE]")
    print("                txoff       (turns TCP tx messages off)            [parameter = NONE]")
    print("                down        (puts CAN interface down)              [parameter = NONE]")
    print("                up          (puts CAN interface up)                [parameter = NONE]")
    print("                reset       (down and up command)                  [parameter = NONE]")
    print("                setbitrate  (sets bitrate of interface)            [parameter = bitrate value]")
    print("                busload     (estimates busload using can-utils)    [parameter = NONE]")
    print("                rxmsgs      (shows number of messages received)    [parameter = NONE]")
    print("                txmsgs      (shows number of messages transmitted) [parameter = NONE]")
    print("\n")
    print("rxon/txon/rxoff/txoff tell the server to open/close ports to receive (rx) or transmit (tx) CAN messages\n")
    print("rxmsgs/txmsgs show number of messages received/transmitted since the TCP connection was started.")
    print("rxmsgs/txmsgs will return 0 if ports are down or if no messages have been received/transmitted.\n")

SERVER_IP = "127.0.0.1"
SERVER_PORT = 2319
MAX_CAN_PER_TCP = 89
CAN_ID_CANGEN = 0x98FEBF0B
DLC_CANGEN = 8
DELAY_BETWEEN_MSGS = 1 #seconds between TCP packets so buffer overflow doesn't happen

canInterfaces = {'can0': b'\x00', 'can1': b'\x01', 'any': b'\xFF'} #dictionary mapping interface name to byte value for tcp packet

canCommands = {'rxon':   [b'\x00',0],  'rxoff':  [b'\x01',0], 'txon':       [b'\x02',0], 'txoff':   [b'\x03',0], 'down':   [b'\x04',0],\
               'up' :    [b'\x05',0],   'reset': [b'\x06',0], 'setbitrate': [b'\x07',3], 'busload': [b'\x08',0], 'rxmsgs': [b'\x09',0],
               'txmsgs': [b'\x10',0]} #dictionary correlating command line abbreviation with list of byte value of tcp packet to send and the number of bytes for parameters

canPorts = {'can0': 2321, 'can1': 2323} # ports used for receiving CAN servers

try:
    if len(sys.argv) > 2 and len(sys.argv) < 5: #if there are two arguments but no more than 4, assuming 1 parameter
        canIntf = sys.argv[1]
        canComm = sys.argv[2]
        if canComm == 'cangen': #transmitting tcp packets of CAN messages, any is not functional here. use multiple instances if needed
            j = 0
            tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                tcpSock.connect((SERVER_IP, canPorts[canIntf]))
            except OSError:
                print("Could not connect to TCP Socket.")
            except KeyError:
                print("Interface not found. Any is not an acceptable interface on this command.")
            while True: #procedural cangen that transmits fixed ID with incrementing payload
                ethData = (MAX_CAN_PER_TCP).to_bytes(1, 'little') #num frames to transmit
                for i in range(MAX_CAN_PER_TCP):
                    ethData = ethData + (CAN_ID_CANGEN).to_bytes(4, 'little') + (DLC_CANGEN).to_bytes(1, 'little') + (0).to_bytes(3, 'little') #padded bytes
                    counter = j*MAX_CAN_PER_TCP + i
                    ethData = ethData + (counter).to_bytes(8, 'big')
                #ethData frame ready
                print("Sending frame of CAN messages")
                print(str(ethData) + str(len(ethData)))
                tcpSock.send(ethData)
                time.sleep(DELAY_BETWEEN_MSGS)
                ethData = b''

                j += 1


        if canCommands[canComm][1] > 0:
            try:
                parameter = int(sys.argv[3]).to_bytes(canCommands[canComm][1], byteorder = 'big') #sets parameter bytes of message based off number of bytes of parameters
            except ValueError:
                printHelp()
                sys.exit()
        else:
            if len(sys.argv) > 3: #parameters given when none should be given
                printHelp()
                sys.exit()
            parameter = b''

        ethData = canInterfaces[canIntf] + canCommands[canComm][0] + parameter #bytes of message to send
    else: #not enough or too many arguments
        printHelp()
        sys.exit()
except KeyError: # no command/interface exists
    printHelp()
    sys.exit()
except IndexError:
    printHelp()
    sys.exit()

print("\nSending {}".format(ethData))
print("\nSending Control Message to IP Address {} on Port {}.\n".format(SERVER_IP, SERVER_PORT))
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcpSocket.connect((SERVER_IP, SERVER_PORT))
except OSError:
    print("Could not connect TCP Socket. Make sure SERVER_IP is correct.")
    sys.exit()

tcpSocket.send(ethData)



