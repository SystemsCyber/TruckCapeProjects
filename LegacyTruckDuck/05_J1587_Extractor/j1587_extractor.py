#!/usr/bin/env python3

# J1587Driver is a higher-level version of the J1708Driver. While J1708Driver only allows you to send
# raw J1708 messages, J1587Driver abstracts away some details. First, import J1587Driver the same way
# that we imported J1708Driver


# struct is the python library for converting raw binary data (like we get from the network). We'll need
# it for decoding some of the network messages.
import struct


def decode_comp_id(byte_string):
    '''
    Function for decoding component ID information.
    '''
    #component ID messages as we receive them are encoded as follows: MID,f3,n,MID,<data>
    # MID: the MID of the device sending the message
    #F3: The PID we're requesting, in hex
    #n: the amount of data in the message
    #data: a list of ASCII characters

    #Here we access an element of a list or string by its index. Remember that we start counting at 0,
    #so this is the 3rd list element
    data_len = byte_string[2]
    
    source_mid = byte_string[3]
    
    # This is a list slice. Using a similar syntax for accessing single elements, we can grab a range
    # of elements. The syntax is list[start_index:end_index], but start_index is *inclusive* and
    # end_index is *exclusive*
    data = byte_string[4:4+data_len-1]

    return str(data,'ascii')

def decode_vin(byte_string):
    '''
    Function for decoding Vehicle Identification (VIN)
    '''
    #VIN messages as we receive them are encoded as follows: MID,ed,n,<data>
    #MID: the MID of the device sending the message
    #ed: the PID we're requesting, in hex
    #n: the amount of data in the message
    #data: a list of ascii characters

    data_len = byte_string[2]
    data = byte_string[3:3+data_len]

    return str(data, 'ascii')

def decode_trip_distance(byte_string):
    '''
    Function for decoding trip distance
    '''
    #Trip distance messages as we get them are encoded as follows: MID,f4,n,a,b,c,d
    #MID: the MID of the device sending the message
    #f4: the PID we're requesting, in hex
    #n: the number of data bytes; in this case, always 4
    #a,b,c,d: data bytes, to be interpreted as a 32-bit unsigned int

    data_len = byte_string[2]

    #Here we use the struct module to unpack 4 bytes into a single integer.
    #The '<' means 'little-endian', and 'L' means 4-byte unsigned int
    trip_distance_raw = struct.unpack('<L', byte_string[3:3+data_len])[0]
    # here we apply the scaling factor given in the standard
    trip_distance_scaled = trip_distance_raw * 0.1

    return trip_distance_scaled

def decode_vehicle_distance(byte_string):
    '''
    Function for decoding vehicle distance
    '''
    # Fill in your own decoding here, just like decode_trip_distance
    # Total Vehicle Distance is encoded as follows: MID,f5,n,a,b,c,d



# Next, create an instance of J1587Driver with the argument 0xAC; this is the MID we'll use to broadcast
# and receive. Call it driver



#here we designate a list of PIDs; it's currently populated with PID 243, Component Identification.
#Add the PIDs 237 (VIN), 244 (Trip Distance), and 245 (Total Vehicle Distance) to the list
#
pids = [243, ]

for pid in pids:
    msg = driver.request_pid(0x80, pid)
    #Depending on which PID we're using, decode with the appropriate function
    if msg is None:
        print("PID {} is not supported by this ECM.".format(pid))
        continue #"continue" means move on to the next thing in the loop
    if pid == 243:
        formatted_output = decode_comp_id(msg)
    elif pid == :#Insert the PID for VIN here
        formatted_output = decode_vin(msg)
    elif pid == :#Insert the PID for Trip Distance here
        formatted_output = decode_trip_distance(msg)
    elif pid == :#Insert the PID for Vehicle Distance here
        formatted_output = decode_vehicle_distance(msg)
    else:#We should never hit this
        continue

    print(formatted_output)
