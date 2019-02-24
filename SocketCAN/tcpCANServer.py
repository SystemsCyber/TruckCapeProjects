#!/usr/bin/python3

import socket

SERVER_IP = "127.0.0.1"
try:
	SERVER_IP = socket.gethostbyname(socket.gethostname()) #gets IP address of machine this is running on
except Exception as e:
	print("Could not get this machine's IP address, defaulting to 127.0.0.1")
SERVER_PORT = 2319
BUFFER_SIZE = 10 #max amount of data to receive

print('---------------------------------------------------------------------')
print("\nHosting TCP server for CAN data at IP Address {} on Port {}".format(SERVER_IP, SERVER_PORT))
print('---------------------------------------------------------------------')

# ***Control message format for received messages on SERVER_PORT***
# [ Interface | Command | Parameters]
#  -> Interface (1 byte) maps to value of interface name found in canInterfaces dict
#  -> Command (1 byte) maps to a command for the specific interface
#  -> Parameters (variable) bytes necessary for the given command

canInterfaces = {0x00: 'can0', 0x01: 'can1', 0xFF: 'any'} #dict for interface byte value to name
canCommands = {0x00: ['stream tcp socket rx on', 0], 0x01: ['stream tcp socket rx off', 0],    0x02: ['stream tcp socket tx on', 0], 0x03: ['stream tcp socket tx off', 0],\
               0x04: ['interface down', 0],          0x05: ['interface up', 0],                0x06: ['interface reset', 0],         0x07: ['change bitrate', 3],\
               0x08: ['CAN busload', 0],             0x09: ['transferred rx CAN messages', 0], 0x10: ['transferred tx CAN messages', 0]}
 #dict for command byte value to dict of {name: number of bytes of parameter}
canPorts = {'can0': [2320,2321], 'can1': [2322, 2323]} #dict for the ports used for each interface. key is interface, value is list of [rxPort, txPort]
#rx is received messages from CAN interface, tx is CAN messages transmitted to CAN interface

parameterSizes = {'stream tcp socket'}

tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	tcpSocket.bind((SERVER_IP, SERVER_PORT))
except OSError:
	print("Could not bind TCP Socket.")
	sys.exit()
tcpSocket.listen(1)
#conn, addr = tcpSocket.accept()
#print("Connection Address:",addr)

while True:
	conn, addr = tcpSocket.accept()
	print("Received control message.")
	print("Connection Address:",addr)
	ethData = conn.recv(BUFFER_SIZE)
	print("Data:", ethData)
	if not ethData: 
		print("EMPTY"); # keeps server open on no data messages
		continue;
	try:
		canIntf = canInterfaces[ethData[0]]
	except KeyError:
		print("Unknown Interface")
	try:
		command, numParamBytes = canCommands[ethData[1]] #stores command name and number of bytes for parameters
	except KeyError:
		print("Unknown Command")
	#command, paramSize = canCommands[ethData[1]]

	print("Interface: ", canIntf)
	print("Command: ", command, '\n')
conn.close()