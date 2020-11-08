#!/usr/bin/env python3

#We import J1939Driver the saem way that we imported J1708Driver and J1587Driver
from hv_networks import J1939Driver

#import the struct module
import struct

# TODO: write a function to decode PGN 0xfee5. Call it decode_fee5, and take one argument "data"
def decode_fee5(data):
    '''
    Function to decode PGN 0xfee5
    '''
    #According to the J1939-71 standard, the format of the data is AAAABBBB, where
    #AAAA is a 4-byte number indicating engine hours and BBBB is a 4-byte number
    #indicating engine revolutions.

    #first, we decode the first 4 bytes as total engine hours
    engine_hours_raw = struct.unpack("<L", data[0:4])[0]
    #Now we apply the scaling factor described in the standard
    engine_hours_scaled = engine_hours_raw * 0.05

    #Next, we decode the next 4 bytes as total engine revolutions
    engine_revolutions_raw = struct.unpack("<L", data[4:8])[0]
    #Now we apply the scaling factor described in the standard
    engine_revolutions_scaled = engine_revolutions_raw * 1000

    return (engine_hours_scaled, engine_revolutions_scaled)

# Create an instance of the J1939Driver class, with the argument interface='can1'. Save it as a variable named driver
driver = J1939Driver.J1939Driver(interface='can1')

# declare a list of PGNS to request containing the following:
# 0xfeeb (component ID), 0xfeec (VIN), 0xfee5 (Engine Hours + Engine Revolutions)
# call it pgn_list

pgn_list = [0xfeeb, 0xfeec, 0xfee5]

for pgn in pgn_list:
    #This demonstrates a function that returns multiple values.
    data = driver.request_pgn(pgn, src_addr=0)
    if data is None:
        print("PGN {} not supported".format(pgn))
        continue
    if pgn == 0xfee5:
        print(decode_fee5(data))
    else:
        print(data)
