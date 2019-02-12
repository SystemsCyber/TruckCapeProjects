#!/usr/bin/python3

import time
import socket
import struct
import sys

# Open a socket and bind to it from SocketCAN
sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_ERR_FILTER, socket.CAN_ERR_MASK) #allows socket to receive error frames
# The interface can be seen from the command prompt (ifconfig)
# The can channel must be configured using the ip link commands
interface = "can1"

# Bind to the interface
try:
    sock.bind((interface,))
except OSError:
    print("Could not bind to interface '%s'\n" % interface)
    sys.exit()

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
# Unsigned Long Integer (little endian), unsigned char (byte), three pad bytes, eight chars (bytes)
# Note: this is 16 bytes


# These are defined in can.h of the Linux kernel sources
# e.g. https://github.com/torvalds/linux/blob/master/include/uapi/linux/can.h
print("socket.CAN_EFF_MASK = 0x{:08X}".format(socket.CAN_EFF_MASK))
print("socket.CAN_EFF_FLAG = 0x{:08X}".format(socket.CAN_EFF_FLAG))
print("socket.CAN_RTR_FLAG = 0x{:08X}".format(socket.CAN_RTR_FLAG))
print("socket.CAN_ERR_FLAG = 0x{:08X}".format(socket.CAN_ERR_FLAG))

# Enter a loop to read and display the data
while True:
	can_packet = sock.recv(16) 
	can_id, can_dlc, can_data = struct.unpack(can_frame_format, can_packet)

	extended_frame = bool(can_id & socket.CAN_EFF_FLAG)
	error_frame = bool(can_id & socket.CAN_ERR_FLAG)
	remote_tx_req_frame = bool(can_id & socket.CAN_RTR_FLAG)
	
	if error_frame:
		can_id &= socket.CAN_ERR_MASK
		can_id_string = "{:08X} (ERROR)".format(can_id)
	else: #Data Frame
		if extended_frame:
			can_id &= socket.CAN_EFF_MASK
			can_id_string = "{:08X}".format(can_id)
		else: #Standard Frame
			can_id &= socket.CAN_SFF_MASK
			can_id_string = "{:03X}".format(can_id)
		
	if remote_tx_req_frame:
		can_id_string = "{:08X} (RTR)".format(can_id)
	
	hex_data_print = ' '.join(["{:02X}".format(can_byte) for can_byte in can_data])
	print("{:12.6f} {} [{}] {}".format(time.time(), can_id_string, can_dlc, hex_data_print))
