import socket

SERVER_IP = "127.0.0.1"
try:
	SERVER_IP = socket.gethostbyname(socket.gethostname()) #gets IP address of machine this is running on
except Exception as e:
	print("Could not get this machine's IP address, defaulting to 127.0.0.1")
SERVER_PORT = 2319
BUFFER_SIZE = 10 #max amount of data to receive

# ***Control message format for received messages on SERVER_PORT***
# [ Interface | Command | Parameters]
#  -> Interface (1 byte) maps to value of interface name found in canInterfaces dict
#  -> Command (1 byte) maps to a command for the specific interface
#  -> Parameters (variable) bytes necessary for the given command

canInterfaces = {0x00: 'can0', 0x01: 'can1', 0xFF: 'any'} #dict for interface byte value to name
canCommands = {0x00: {'stream tcp socket rx on': 0}, 0x01: {'stream tcp socket rx off': 0},    0x02: {'stream tcp socket tx on': 0}, 0x03: {'stream tcp socket tx off': 0},\
               0x04: {'interface down': 0},          0x05: {'interface up': 0},                0x06: {'interface reset', 0},         0x07: {'change bitrate', 3},\
               0x08: {'CAN busload': 0},             0x09: {'transferred rx CAN messages': 0}, 0x10: {'transferred tx CAN messages', 0}}
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
conn, addr = tcpSocket.accept()
print("Connection Address:",addr)

while True:
	ethData = conn.recv(BUFFER_SIZE)
	if not ethData: break;
	print("Received control message.\n" + ethData)
	canIntf = ethData[0]
	command = ethData[1]
	#command, paramSize = canCommands[ethData[1]]

	print("Interface: ", canIntf)
	print("Command: ", command)
conn.close()