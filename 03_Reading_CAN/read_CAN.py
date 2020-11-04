#!/usr/bin/env python3

# This is called an import statement. It allows us to bring code written by
# other people into our program.
# There are three libraries we'll need
import socket
import struct
import time


# There are two options to make this program work. 
# 1. Connect the TruckCape to an actual Truck
# 2. Read CAN from a vcan channel that is being populated with canplayer

# Open a socket and bind to it from SocketCAN
sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
interface = "vcan0"

# Bind to the interface
sock.bind((interface,))

# The basic CAN frame structure and the sockaddr structure are defined
#   in include/linux/can.h:
#     struct can_frame {
#             canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
#             __u8    can_dlc; /* frame payload length in byte (0 .. 8) */
#             __u8    __pad;   /* padding */
#             __u8    __res0;  /* reserved / padding */
#             __u8    __res1;  /* reserved / padding */
#             __u8    data[8] __attribute__((aligned(8)));
#     };   

# To match this data structure, the following struct format can be used:
can_frame_format = "<LB3x8s"

#Here we are going to read 100 messages.
for i in range(100):
    # The following block program execution until a new message arrives
    can_packet = sock.recv(16)
    
    # using the struct library, unpack the 16 bytes that made up the SocketCAN message
    # This includes the CAN arbitration ID, the data length code, and the data bytes
    can_id, can_dlc, can_data = struct.unpack(can_frame_format, can_packet)
    
    #Look to see if the extended can frame bit is set 
    extended_frame = bool(can_id & socket.CAN_EFF_FLAG)
    if extended_frame:
        #Pass only the bits that make up the extended frame id
        can_id &= socket.CAN_EFF_MASK
        #Convert this integer into a 4-byte hex character representation
        can_id_string = "{:08X}".format(can_id)
    else: #Standard Frame
        can_id &= socket.CAN_SFF_MASK
        can_id_string = "{:03X}".format(can_id)
    
    #Print the valid data bytes to a string using a list comprehension
    hex_data_string = ' '.join(["{:02X}".format(b) for b in can_data[:can_dlc]])
    
    # Display the data in the candump format
    # The format statement enables the display of string data.
    print("{} {} [{}] {}".format(interface, can_id_string, can_dlc, hex_data_string))
    
