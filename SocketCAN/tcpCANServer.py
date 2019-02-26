#!/usr/bin/python3

import socket
from multiprocessing import Process, Value

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

def rxClient(interface, isAlive): #method called for transferring CAN messages read from vehicle network and sending to a server via tcp client
	while isAlive.value: #shared variable, when non-zero it's true, 0 is false. Client is open until commanded to close on command port
		#keep client alive and read messages, pack them into ethernet frame, and send
		#if timeout, send 0 messages from CAN and pad the bytes
		print("RX Client Active:", interface)
	return 0

# INSERT CODE to do tx CAN transfer here
def txServer(interface, isAlive):
	while isAlive.value: #shared variable when non-zero is true, 0 is false. Server open until commanded to close on command port
		#keep server alive waiting for tcp messages containing CAN data
		#read the desginated number of frames decided by first byte in message, and send on specified CAN interface
		print("TX Server Active:", interface)
	return 0


tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

intfOrder = ['can0', 'can1'] #should be updated if more interfaces are added or process order storing in list needing to be different
rxProcesses = [None for i in range(len(canInterfaces)-1)]
txProcesses = [None for i in range(len(canInterfaces)-1)] #lists to store rx and tx clients/server processes. Assumes processes in order of intfOrder, excludes any
keepRxAlive = [Value('i', 0) for i in range(len(canInterfaces) -1)] #list of shared variables. Used to determine if rx client should still be running
keepTxAlive = [Value('i', 0) for i in range(len(canInterfaces) -1)] #list of shared variables. Used to determine if tx server should still be up


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

	if command == 'stream tcp socket rx on': #turn on stream for tcp client to send CAN frames
		if canIntf == 'any':
			for i in range(len(intfOrder)): #for all interfaces
				print("Turning on client port to receive CAN frames connecting to port", canPorts[intfOrder[i]][0])
				print("Start RX Client for", intfOrder[i],'\n')
				#start processes with intfOrder as parameter
				keepRxAlive[i].value = 1 #set shared variable to 1
				rxProcesses[i] = Process(target = rxClient, args=(intfOrder[i], keepRxAlive[i])) #create process passing interfacename and shared value
				rxProcesses[i].start() #start the process
		else:
			print("Turning on client port to receive CAN frames connecting to port", canPorts[canIntf][0]) 
			print("Start RX Client for", canIntf,'\n')
			#start process passing canIntf as parameter
			for i,intf in enumerate(intfOrder): #used to find index of interface in intfOrder
				if intf == canIntf:
					print("Found the chosen interface", intf)
					keepRxAlive[i].value = 1 #set shared variable
					rxProcesses[i] = Process(target = rxClient, args=(intf, keepRxAlive[i])) #create process
					rxProcesses[i].start() #start process
	
	elif command == 'stream tcp socket rx off': #turn off stream for tcp client to send CAN frames
		print("Turning off client port to receive CAN frames")
		if canIntf == 'any':
			for i in range(len(intfOrder)): #for all interfaces
				try:
					keepRxAlive[i].value = 0 #set shared value to 0
					rxProcesses[i].join() #wait for the process to end
				except: #error handle if join doesn't work
					print("Did you start the rx client on",intfOrder[i]+"?")
		else:
			for i,intf in enumerate(intfOrder): #find index of given interface in intfOrder
				if intf == canIntf:
					try:
						keepRxAlive[i].value = 0 #set shared value to 0
						rxProcesses[i].join() #wait for process to end
					except: #error handle for join
						print("Did you start the rx client on",intf+"?")

	elif command == 'stream tcp socket tx on':
		if canIntf == 'any':
			for i in range(len(intfOrder)):
				print("Turning on server port to send CAN frames on port", canPorts[intfOrder[i]][1])
				print("Start TX Server for",intfOrder[i],'\n')
				#start processes with each interface name and value to decide if server should still be running
				keepTxAlive[i].value = 1
				txProcesses[i] = Process(target = txServer, args=(intfOrder[i], keepTxAlive[i]))
				txProcesses[i].start()
		else:
			print("Turning on server port to send CAn frames on port", canPorts[canIntf][1])
			print("Start TX Server for",canIntf,'\n')
			#start process passing canIntf and value to determine if server should still be running
			for i, intf in enumerate(intfOrder):
				if intf == canIntf:
					print("Found the chosen interface", intf)
					keepTxAlive[i].value = 1
					txProcesses[i] = Process(target = txServer, args = (intf, keepTxAlive[i]))
					txProcesses[i].start()
	elif command == 'stream tcp socket tx off':
		print("Turning off server port to send CAN frames")
		if canIntf == 'any':
			for i in range(len(intfOrder)):
				try:
					keepTxAlive[i].value = 0
					txProcesses[i].join()
				except:
					print("Did you start the tx client on", intfOrder[i]+'?')
		else:
			for i,intf in enumerate(intfOrder):
				if intf == canIntf:
					try:
						keepTxAlive[i].value = 0
						txProcesses[i].join()
					except:
						print("Did you start the tx client on", intf, '?')
conn.close()