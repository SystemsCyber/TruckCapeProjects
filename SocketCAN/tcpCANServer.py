#!/usr/bin/python3

import time
import socket
import struct
import sys
import uuid

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
can_frame_format = "<LL8s"
# Unsigned Long Integer (little endian), unsigned char (byte), three pad bytes, eight chars (bytes)
# Note: this is 16 bytes


# These are defined in can.h of the Linux kernel sources
# e.g. https://github.com/torvalds/linux/blob/master/include/uapi/linux/can.h
"""print("socket.CAN_EFF_MASK = 0x{:08X}".format(socket.CAN_EFF_MASK))
print("socket.CAN_EFF_FLAG = 0x{:08X}".format(socket.CAN_EFF_FLAG))
print("socket.CAN_RTR_FLAG = 0x{:08X}".format(socket.CAN_RTR_FLAG))
print("socket.CAN_ERR_FLAG = 0x{:08X}".format(socket.CAN_ERR_FLAG))
print("socket.CAN_ERR_FLAG = 0x{:08X}".format(socket.CAN_SFF_MASK))"""

CAN_EFF_MASK = 0x1FFFFFFF #assigned to remove socketCAN dependencies, values obtained by above print statements using socketCAN
CAN_EFF_FLAG = -0x80000000
CAN_RTR_FLAG = 0x40000000
CAN_ERR_FLAG = 0x20000000
CAN_ERR_MASK = 0x1FFFFFFF
CAN_SFF_MASK = 0x000007FF #standard CAN format 

#setup tcp server for CAN data reception
SERVER_IP = "127.0.0.1"
try:
	SERVER_IP = socket.gethostbyname(socket.gethostname()) #gets IP address of machine this is running on
except Exception as e:
	print("Could not get this machine's IP address, defaulting to 127.0.0.1")
SERVER_PORT = 2319
BUFFER_SIZE = 1425 #maximum amount of data to receive at once for 89 CAN frames and 1 counter byte 16*89+1 = 1425
SIZE_OF_CAN_FRAME = 16
COUNTER_OFFSET = 1 #number of bytes at the start of ethernet packet not part of a CAN frame
DIRECTORY_NAME = '' #change to appropriate local directory of form 'directoryName/', empty string stores in same directory as tcpCANServer.py
LOG_FILE_NAME = 'canlog_{}.txt'.format(uuid.uuid4()) #uuid4 generates a random universally unique identifier
print('---------------------------------------------------------------------')
print("\nHosting TCP server for CAN data at IP Address {} on Port {}".format(SERVER_IP, SERVER_PORT))
print('---------------------------------------------------------------------')

tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	tcpSocket.bind((SERVER_IP, SERVER_PORT))
except OSError:
	print("Could not bind TCP Socket.")
	sys.exit()
tcpSocket.listen(1)
conn, addr = tcpSocket.accept()
print("Connection Address:",addr)

with open (DIRECTORY_NAME+LOG_FILE_NAME, 'w') as file:
	while True:
		ethData = conn.recv(BUFFER_SIZE)
		if not ethData: break;
		print("Received", int(ethData[0]), "CAN frames.")
		for i in range(int(ethData[0])):
			#gets individiual CAN packet
			can_packet = ethData[SIZE_OF_CAN_FRAME*i + COUNTER_OFFSET: SIZE_OF_CAN_FRAME*i + SIZE_OF_CAN_FRAME + COUNTER_OFFSET]
			can_id, can_dlc_and_microTimer, can_data = struct.unpack(can_frame_format, can_packet)

			can_dlc = (can_dlc_and_microTimer & 0x000000FF)  #first byte is dlc b/c little endian
			can_microTimer = (can_dlc_and_microTimer & 0xFFFFFF00) >> 8 #first three bytes are microseconds timestamp

			extended_frame = bool(can_id & CAN_EFF_FLAG)
			error_frame = bool(can_id & CAN_ERR_FLAG)
			remote_tx_req_frame = bool(can_id & CAN_RTR_FLAG)
	
			if error_frame:
				can_id &= CAN_ERR_MASK
				can_id_string = "{:08X} (ERROR)".format(can_id)
			else: #Data Frame
				if extended_frame:
					can_id &= CAN_EFF_MASK
					can_id_string = "{:08X}".format(can_id)
				else: #Standard Frame
					can_id &= CAN_SFF_MASK
					can_id_string = "{:03X}".format(can_id)
		
			if remote_tx_req_frame:
				can_id_string = "{:08X} (RTR)".format(can_id)
	
			hex_data_print = ' '.join(["{:02X}".format(can_byte) for can_byte in can_data])
			print("{:12.2f} {} [{}] {}".format(can_microTimer, can_id_string, can_dlc, hex_data_print))
			file.write("{:12.2f} {} [{}] {}\n".format(can_microTimer, can_id_string, can_dlc, hex_data_print))
	conn.close()

