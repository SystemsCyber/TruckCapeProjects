#!/usr/bin/env python3

#First, import J1939Driver the saem way that we imported J1708Driver and J1587Driver




# Here, we're re-using the binary_string_to_hex function from the J1708 logger.
# Usually we would put this kind of function in a separate file and import it
# (to save on copy and pasting) but that's beyond the scope of this class

#we've made one modification so that this looks nicer as part of CSV output
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

    return ' '.join(message_hex_list)

#These two functions format various numerical values so that they can be written to the screen or a file
def format_pgn(pgn):
    return "{:04x}".format(pgn)

# Here, define another function called format_addr to output a 2 hex character string. HINT: just replace
# 4 with 2 in the format string


#Create an instance of the J1939Driver class, with the argument interface='can1'. Save it as a variable named driver


for i in range(10):
    #This demonstrates a function that returns multiple values.
    (pgn, priority, src_addr, dst_addr, data) = driver.read_message()
    values_to_print = []
    formatted_pgn = format_pgn(pgn)
    formatted_src = format_addr(src_addr)
    formatted_dst = format_addr(dst_addr)
    formatted_data = binary_string_to_hex(data)
    print(','.join((formatted_pgn, formatted_src, formatted_dst, formatted_data)))
