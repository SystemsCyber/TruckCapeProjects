#!/usr/bin/env python3

#Import J1939Driver the saem way that we imported J1708Driver and J1587Driver


#import the struct module
import struct

# TODO: write a function to decode PGN 0xfee5. Call it decode_fee5, and take one argument "data"
# Make it return a tuple of (scaled_engine_hours, scaled_engine_revolutions)


# Create an instance of the J1939Driver class, with the argument interface='can1'. Save it as a variable named driver


# declare a list of PGNS to request containing the following:
# 0xfeeb (component ID), 0xfeec (VIN), 0xfee5 (Engine Hours + Engine Revolutions)
# call it pgn_list



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
