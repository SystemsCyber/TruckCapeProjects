#!/usr/bin/python3

import socket
import sys

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

canInterfaces = {'can0': b'\x00', 'can1': b'\x01', 'any': b'\xFF'} #dictionary mapping interface name to byte value for tcp packet

canCommands = {'rxon':   [b'\x00',0],  'rxoff':  [b'\x01',0], 'txon':       [b'\x02',0], 'txoff':   [b'\x03',0], 'down':   [b'\x04',0],\
               'up' :    [b'\x05',0],   'reset': [b'\x06',0], 'setbitrate': [b'\x07',3], 'busload': [b'\x08',0], 'rxmsgs': [b'\x09',0],
               'txmsgs': [b'\x10',0]} #dictionary correlating command line abbreviation with list of byte value of tcp packet to send and the number of bytes for parameters

try:
    if len(sys.argv) > 2 and len(sys.argv) < 5: #if there are two arguments but no more than 4, assuming 1 parameter
        canIntf = sys.argv[1]
        canComm = sys.argv[2]
        if canCommands[canComm][1] > 0:
            parameter = int(sys.argv[3]).to_bytes(canCommands[canComm][1], byteorder = 'big') #sets parameter bytes of message based off number of bytes of parameters
        else:
            if len(sys.argv) > 3: #parameters given when none should be given
                printHelp()
                sys.exit()
            parameter = b'\x00'

        ethData = canInterfaces[canIntf] + canCommands[canComm][0] + parameter #bytes of message to send
        print("Sending {}".format(ethData))
    else: #not enough or too many arguments
        printHelp()
        sys.exit()
except KeyError: # no command/interface exists
    printHelp()
    sys.exit()
except IndexError:
    printHelp()
    sys.exit()



print("Sending Control Message to IP Address {} on Port {}.", SERVER_IP, SERVER_PORT)

tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    pass #tcpSocket.connect((SERVER_IP, SERVER_PORT))
except OSError:
    print("Could not connect TCP Socket. Make sure SERVER_IP is correct.")
    sys.exit()



