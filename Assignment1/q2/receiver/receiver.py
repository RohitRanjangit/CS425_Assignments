# please do not use any library
import sys
previous_message=""

poly = '10011'

def generate_crc_checkbit(raw_msg):
    """This function will generate degree of poly-1 
    bit  crc_check bit"""
    raw_msg = raw_msg + (len(poly)-1)*'0'
    pick = len(poly)
    temp = raw_msg[0:pick]
    while pick < len(raw_msg):
        if temp[0]=='1':
            temp = '{0:b}'.format(int(temp,2)^int(poly,2))
            temp = '0'*(len(poly)-1-len(temp)) + temp
            temp = temp + raw_msg[pick]
        else:
            temp = temp[1:] + raw_msg[pick]
        pick = pick+1
    if temp[0]=='1':
        temp = '{0:b}'.format(int(temp,2)^int(poly,2))
        temp = '0'*(len(poly)-1-len(temp)) + temp
    else:
        temp = temp[1:]
    return '0'*(len(poly)-1-len(temp)) + temp


filename=''
if len(sys.argv) >=2:
    filename = sys.argv[1]
else:
    filename = "input.txt"

with open(filename) as input:
    lmsg = input.readlines()
    for msg in lmsg:
        msg = msg[:-1]
        if msg == previous_message:
            print("duplicate", end= ' ')
            previous_message = msg
        else:
            previous_message = msg
            msg = msg[:-1]
            # print(msg)
            crc_bits = msg[-4:]
            # print(crc_bits)
            msg = msg[:-4]
            # print(msg)
            if crc_bits != generate_crc_checkbit(msg):
                print("corrupt", end= ' ')
            else:
                for  i in range(0,len(msg),8):
                    curr_char_ascii = int(msg[i:min(i+8,len(msg))],2)
                    print(chr(curr_char_ascii), end='')
                print('', end=' ')
print() 