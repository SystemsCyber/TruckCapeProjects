#!/usr/bin/python3

import socket
from multiprocessing import Process, Value
import time
import select

SERVER_IP = "127.0.0.1"
try:
	SERVER_IP = socket.gethostbyname(socket.gethostname()) #gets IP address of machine this is running on
except Exception as e:
	print("Could not get this machine's IP address, defaulting to 127.0.0.1")
SERVER_PORT = 2319 #control server port
BUFFER_SIZE = 1425 #max amount of data to receive
TIMEOUT = 5 # number of seconds before sending padded tcp frame in cases of low or non-existant traffic
MAX_CAN_PER_TCP = 89 #the max number of allowed CAN frames in each TCP packet
MIN_ETH_PAYLOAD = 46 #min number of payload bytes needed for ethernet frame
BYTES_PER_CANFRAME = 16
COUNTER_OFFSET = 1

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
 #dict for command byte value to list of [name, number of bytes of parameter]
canPorts = {'can0': [2320,2321], 'can1': [2322, 2323]} #dict for the ports used for each interface. key is interface, value is list of [rxPort, txPort]
#rx is received messages from CAN interface, tx is CAN messages transmitted to CAN interface

def rxClient(interface, isAlive, address): #method called for transferring CAN messages read from vehicle network and sending to a server via tcp client
	canSock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
	canSock.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_ERR_FILTER, socket.CAN_ERR_MASK) #allows socket to receive error frames
	tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		canSock.bind((interface,))
	except:
		print("Could not bind to interface '%s' \n" % interface)
		isAlive.value = 0 #stop process
	try:
		tcpSock.connect((address[0], address[1])) #address contains [ipAddress, portnumber] of server to connect to
	except:
		print("Could not connect TCP Socket at {}:{}".format(address[0], address[1]))
		isAlive.value = 0 #stop process

	startTime = time.time() #start time of data transfer
	currentTime = time.time() #current time in seconds
	lastCANReadTime = time.time() #store time of last read message starting at current time
	SEC_TO_MICROS = 1000000 #coverts seconds to micros by multiplication
	ethData = b'' # used to store payload of tcp packet
	numCANFrames = 0 #stores num of CAN frames in specific TCP packet

	while isAlive.value: #shared variable, 1 true, 0 is false. Client is open until commanded to close on command port
		#keep client alive and read messages, pack them into ethernet frame, and send
		while currentTime - lastCANReadTime < TIMEOUT: #loop until timout of CAN messages occurs
			msgSent = False #keeps track if a full message has been sent
			currentTime = time.time()
			while select.select([canSock],[],[],1)[0]: #while a can frame is on the interface
				canFrame = canSock.recv(16) #just append the raw bytes from the socket, no need to unpack on this end
				numCANFrames += 1 #increment num of CAN frame counter
				lastCANReadTime = time.time() #resets timer to indicate message just was read
				if int((lastCANReadTime - startTime)*SEC_TO_MICROS) >= 0xFFFFFF: startTime = lastCANReadTime #resets start time to rollover timestamp
				microTimer = (int((lastCANReadTime - startTime)*SEC_TO_MICROS)).to_bytes(3, byteorder='little')
				ethData += canFrame[:5] + microTimer + canFrame[8:] #replaces padded bytes with microsecond timer
				if (numCANFrames >= MAX_CAN_PER_TCP):
					ethData = bytes([numCANFrames]) + ethData #concatenates size as first byte of the frame
					print("Sending full frame")
					tcpSock.send(ethData)
					msgSent = True # msg has just been sent. will reset to false after next message is read
					ethData = b''
					numCANFrames = 0
					if not isAlive.value: break; #same as below, breaks from select.select while loop after message is sent
					#only if the process should no longer be alive
			if not isAlive.value and msgSent: break; #breaks out from reading CAN messages if the shared variable says the process is not alive,
			#and if the message has been sent. breaks out of timeout loop
		#if timeout,pad the bytes and send a message
		while len(ethData) < MIN_ETH_PAYLOAD: #more than enough padding
			ethData += b'\x00' #pads frame to min size of eth frame
		ethData = bytes([numCANFrames]) + ethData #appends size as first byte of frame
		print("Sending padded frame")
		tcpSock.send(ethData)
		isAlive.value = 0 #sets value to false to kill itself if no messages on the bus for the timout period
		currentTime = time.time() #resets current time
		lastCANReadTime = time.time() #resets last read time so it can begin reading from vehicle network again

	print("Closing rxClient for", interface, "to port", address[1])
	tcpSock.close()
	return 0

def txServer(interface, isAlive, address): #method called for receiving CAN messages on TCP Server and trasmitting on vehicle network
	canSock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
	canSock.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_ERR_FILTER, socket.CAN_ERR_MASK)
	tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		canSock.bind((interface,))
	except:
		print("Could not bind to interface '%s' \n" % interface)
		isAlive.value = 0 #stop process
	try:
		tcpSock.bind((address[0], address[1])) #address contains [ipAddress, portnumber] of server to connect to
	except Exception as e:
		print("Could not connect TCP Socket at {}:{}\n".format(address[0], address[1]) + str(e))
		isAlive.value = 0 #stop process
	tcpSock.listen(1) #listens for tcp packets to parse and send on vehicle network
	conn, addr = tcpSock.accept()
	print("Connection Address:",addr)
	while isAlive.value: #shared variable when non-zero is true, 0 is false. Server open until commanded to close on command port
		#keep server alive waiting for tcp messages containing CAN data
		ethData = conn.recv(BUFFER_SIZE)
		if not ethData: break;
		#read the desginated number of frames decided by first byte in message, and send on specified CAN interface
		print("Received", int(ethData[0]), "CAN Frames")
		print("Transmitting onto Vehicle Network Interface:", interface)
		for i in range(int(ethData[0])): # for the number of can frames
			can_packet = ethData[i*BYTES_PER_CANFRAME + COUNTER_OFFSET: i*BYTES_PER_CANFRAME + COUNTER_OFFSET + BYTES_PER_CANFRAME] #offset of 1 for the counter, multiply by 16 b/c 16 bytes per
			canSock.send(can_packet)
			#print("CAN FRAME:", str(can_packet))

		#parse messages

		#send on CAN interface

		"""print("TX Server Active:", interface)
		print(address[0]+":"+str(address))"""
	print("Closing txServer for", interface, "on port", address[1])
	tcpSock.close()
	return 0


tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

intfOrder = ['can0', 'can1'] #should be updated if more interfaces are added or process order storing in list needing to be different
rxProcesses = [None for i in range(len(canInterfaces)-1)]
txProcesses = [None for i in range(len(canInterfaces)-1)] #lists to store rx and tx clients/server processes. Assumes processes in order of intfOrder, excludes any
keepRxAlive = [Value('i', 0) for i in range(len(canInterfaces) -1)] #list of shared variables. Used to determine if rx clients should still be running
keepTxAlive = [Value('i', 0) for i in range(len(canInterfaces) -1)] #list of shared variables. Used to determine if tx servers should still be up


try:
	tcpSocket.bind((SERVER_IP, SERVER_PORT))
except OSError:
	print("Could not bind TCP Socket.")
	sys.exit()
tcpSocket.listen(1) #control server listening

while True: #control server open until CTRL+C
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

	print("Interface: ", canIntf)
	print("Command: ", command, '\n')

	if command == 'stream tcp socket rx on': #turn on stream for tcp client to send CAN frames
		if canIntf == 'any':
			for i in range(len(intfOrder)): #for all interfaces
				print("Turning on client port to receive CAN frames connecting to port", canPorts[intfOrder[i]][0])
				print("Start RX Client for", intfOrder[i],'\n')
				#start processes with intfOrder as parameter
				keepRxAlive[i].value = 1 #set shared variable to 1
				rxProcesses[i] = Process(target = rxClient, args=(intfOrder[i], keepRxAlive[i], [addr[0], canPorts[intfOrder[i]][0]])) #create process passing interfacename and shared value
				rxProcesses[i].start() #start the process
		else: #if specific interface
			print("Turning on client port to receive CAN frames connecting to port", canPorts[canIntf][0]) 
			print("Start RX Client for", canIntf,'\n')
			#start process passing canIntf as parameter
			for i,intf in enumerate(intfOrder): #used to find index of interface in intfOrder
				if intf == canIntf:
					print("Found the chosen interface", intf)
					keepRxAlive[i].value = 1 #set shared variable
					rxProcesses[i] = Process(target = rxClient, args=(intf, keepRxAlive[i], [addr[0], canPorts[canIntf][0]])) #create process
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
				txProcesses[i] = Process(target = txServer, args=(intfOrder[i], keepTxAlive[i], [SERVER_IP, canPorts[intfOrder[i]][1]]))
				txProcesses[i].start()
		else:
			print("Turning on server port to send CAn frames on port", canPorts[canIntf][1])
			print("Start TX Server for",canIntf,'\n')
			#start process passing canIntf and value to determine if server should still be running
			for i, intf in enumerate(intfOrder):
				if intf == canIntf:
					print("Found the chosen interface", intf)
					keepTxAlive[i].value = 1
					txProcesses[i] = Process(target = txServer, args = (intf, keepTxAlive[i], [SERVER_IP, canPorts[canIntf][1]]))
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