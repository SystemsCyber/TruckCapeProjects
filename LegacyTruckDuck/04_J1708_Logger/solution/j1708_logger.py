#!/usr/bin/env python3

import sys
from hv_networks import J1708Driver


#This reads command-line arguments to tell the program which filename to write to
if len(sys.argv) < 3:
    print('''USAGE: {} <filename> <number_of_messages>'''.format(sys.argv[0]))
    sys.exit(-1)
else:
    filename = sys.argv[1]
    # command line arguments are always read as strings; to turn it into a number that we can
    # use, we have to tell the interpreter that we want it to be a number by passing it to the
    # int() function
    num_messages = int(sys.argv[2])

# Here, we define a function. functions are a way to define one block of code that we can call
# multiple times. It saves us a lot of typing.

def binary_string_to_hex(binary_string):
    '''
    Take a binary string binary_string and return a comma-separated-value string.
    '''
    # mesage_hex_list is an instnace of a datatype called a list. Lists are ways to group multiple
    # values together.
    message_hex_list = []

    # binary strings are like strings, but if you treat them as a list, the individual elements are
    # 8-bit numbers
    for char in binary_string:
        message_hex_list.append("{:02x}".format(char))

    return ','.join(message_hex_list)

# Now, instantiate an instance of the J1708Driver class with the argument J1708Driver.ECM
# Call it "driver"

driver = J1708Driver.J1708Driver(J1708Driver.ECM)

try:
    logfile = open(filename, 'w')
except:
    print("Could not open {}".format(filename))
    sys.exit(-2)



for i in range(num_messages):
    #read a message from the driver, and store it in the variable msg
    msg = driver.read_message()

    # The raw binary format returned by read_message is great for computers, but it's hard for
    # humans to read. Create a variable called formatted_msg, and use it to store the result of
    # a call to the function binary_hex_to_string with msg as its argument

    formatted_msg = binary_string_to_hex(msg)

    #This is where we write to the file. '\n' is the newline character; it will place each new message
    #on its own line.
    logfile.write(formatted_msg + '\n')
