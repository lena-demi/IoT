import struct
import socket

def hex_to_str(s):
    return bytes.fromhex(s)

# Creating of a dictionaries of Modbus TCP exception and functional codes
dict_exceptions = {
    1: "01: Illegal Function",
    2: "02: Illegal Data Address",
    3: "03: Illegal Data Value",
    4: "04: Server Device Failure",
    5: "05: Acknowledge",
    6: "06: Server Device Busy",
    7: "07: Negative Acknowledge",
    8: "08: Memory Parity Error",
    10: "10: Gateway Path Unavailable",
    11: "11: Gateway Target Device Failed to Respond" 
    }

dict_functional_code = {
    1: "Reading of digital outputs",
    2: "Reading of digital inputs",
    3: "Reading of analog outputs",
    4: "Reading of analog inputs",
    5: "Writing of digital output",
    6: "Writing of analog output",
    15: "Writing of a several digital outputs",
    16: "Writing of a several analog outputs"
    }

# reading of descrete endpoints (functional code 0x01, 0x02)
def read_descrete (data, info):
    print (dict_functional_code[info[4]], ": \n")
    if info[4] == 1: endpoint = "output"
    if info[4] == 2: endpoint = "input"
    # unpack data
    length = int(info[2]) - 2
    n = int(length)
    msg_format = ">"
    for i in range (n):
        msg_format = msg_format + "B"
    data_unpacked = struct.unpack(msg_format, data)
    # get binary data
    x = ""
    for i in range (len(data_unpacked)-1, 0, -1):
        x = x + format(data_unpacked[i], 'b')
    # parse data    
    j=0
    for i in range(len(x)-1, -1, -1):
        j=j+1
        if int(x[i]) == 1: status = "ON"
        else: status = "OFF"
        print ("%s № %d is %s" % (endpoint, j, status))
    print ("Other digital %ss are OFF or do not exist" % (endpoint))

# reading of analog endpoints (functional code 0x03, 0x04)
def read_analog (data, info):
    print (dict_functional_code[info[4]])
    if info[4] == 3: endpoint = "output"
    if info[4] == 4: endpoint = "input"
    # unpack data
    length = int(info[2]) - 3
    n = int(length/2)
    msg_format = ">B"
    for i in range (n):
        msg_format = msg_format + "H"
    data_unpacked = struct.unpack(msg_format, data)
    # parse data
    for i in range (1, len(data_unpacked)):
        print ("%s № %d is %d" % (endpoint, i, int(data_unpacked[i])))
    
# write 1 descrete output (functional code 0x05)
def write_single_descrete (data, info):
    print (dict_functional_code[info[4]])
    data_unpacked = struct.unpack(">HH", data)
    if data_unpacked[1] == 0x0000: status = "OFF"
    elif data_unpacked[1] == 0xFF00: status = "ON"
    else: status = "not written: you are trying to write something incorrect"
    print ("Output № %d\nNew value is %s " %(int(data_unpacked[0]), status))

# write 1 analog output (functional code 0x06)
def write_single_analog (data, info):
    print (dict_functional_code[info[4]])
    data_unpacked = struct.unpack(">HH", data)
    print ("Output № %d\nNew value is %d " %(int(data_unpacked[0]), int(data_unpacked[1])))
    
# write several outputs (functional code 0x0F, 0x10)
def write_several (data, info):
    print (dict_functional_code[info[4]])
    data_unpacked = struct.unpack(">HH", data)
    print ("Writing from output № %d \nNumber of written outputs: %d" %(int(data_unpacked[0]), int(data_unpacked[1])))   

# errors from Modbus TCP
def error (data):
    print("EXCEPTION")
    data_unpacked = struct.unpack(">B", data)
    if data_unpacked[0] in dict_exceptions: print(dict_exceptions[data_unpacked[0]])
    else: print(data_unpacked[0], ": Unknown exception")

# MAIN CODE
while True:
    msg=input("print the Modbus TCP message here:\n")
    info = msg[0:16]
    payload = msg[16:]
    try:
        info_bin = hex_to_str(info)
        data_bin = hex_to_str(payload)
        info_unpacked = struct.unpack(">HHHBB", info_bin)
        transaction_id = info_unpacked[0]
        device_id = info_unpacked[3]
        code = info_unpacked[4]
        print ("\ntransaction id = %d \ndevice id = %d \n" % (transaction_id, device_id))
        if (code &  0x80) == 128: error(data_bin)
        elif (code == 1) or (code == 2): read_descrete(data_bin, info_unpacked)
        elif (code == 3) or (code == 4): read_analog(data_bin, info_unpacked)
        elif (code == 15) or (code == 16): write_several(data_bin, info_unpacked)
        elif (code == 5): write_single_descrete(data_bin, info_unpacked)
        elif (code == 6): write_single_analog(data_bin, info_unpacked)
        else: print("I don't know such code as '%s', try again" % code)
    except:
        print ("Incorrect message, please try again")
    print ("___________________")
