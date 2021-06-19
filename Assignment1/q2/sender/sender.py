from threading import Thread
import time
import socket
import sys

# Please do not change the socket configration
# socket used are blocking in nature

#####################################
##########code here##################
#####################################

poly = '10011'  # polynomial
to = 2  # timeout


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

previous_ack=""

def checkMsg(msg):
    # this is a Receiver side helper function
    # you can change the name of the function if you want
    # checks weather the message is correctly received or not
    # i.e detect error using CRC, return True if no error,else Flase

    #####################################
    #####################################

    msg = msg[0:-1]
    received_crc_check_bit = msg[-4:]
    msg=msg[:-4]
    
    if received_crc_check_bit != generate_crc_checkbit(msg):
        return False
    
    return True

def sender():
    s = socket.socket()
    # print("Socket successfully created")
    port = 12345
    s.bind(('', port))
    # print("socket binded to %s" % (port))
    s.listen(1)
    # print("socket is listening")
    c, addr = s.accept()
    c.settimeout(to)
    

    #####################################
    ##########code here##################
    #####################################
    # take input from input.txt line by line and make sure you send all the messages
    # to the receiver
    
    filename=''
    if len(sys.argv) >=2:
        filename = sys.argv[1]
    else:
        filename = "input.txt"

    with open(filename) as input:
        global previous_ack
        lmsg = input.readlines()
        for msg in lmsg:
            msg = msg[:-1]
            crc_check_bits = generate_crc_checkbit(msg)
            
            flag ='0'
            if previous_ack:
                if previous_ack[-1]=='0':
                    flag='1'
                else:
                    flag='0'
            else:
                flag = '0'
            
            correct_ack = "100" + flag + crc_check_bits
            message = msg+crc_check_bits+flag
            
            try:
                c.sendall(bytes(message, 'utf-8'))
            except:
                print("Some error happend at receiver end")
                return
            received_ack =""
            
            while received_ack != correct_ack:
                try:
                    received_ack = c.recv(1024)
                    received_ack = received_ack.decode('utf-8')
                    if received_ack != correct_ack:
                        print("wrong ack")
                        received_ack=""
                        try:
                            c.sendall(bytes(message, 'utf-8'))
                        except:
                            print("Some error happend at receiver end")
                            return
                except socket.timeout:
                    print("no ack")
                    received_ack=""
                    try:
                        c.sendall(bytes(message, 'utf-8'))
                    except:
                        print("Some error happend at receiver end")
                        return
                except ConnectionResetError:
                    print("Reciever thread exited unwillingly!!")
                    c.close()
                    return
        
            print("message sent")
    #####################################
    #####################################
    c.close()


def receiver():
    time.sleep(.5)
    s = socket.socket()
    port = 12345
    s.connect(('127.0.0.1', port))
    #####################################
    ##########read here##################
    #####################################
    # the receiver function seems to be long however it is just same thing repeated
    # over and over again, so understanding a part will be
    ack1 = "10011000"
    ack0 = "10000011"

    # 1
    #####################################
    msg = s.recv(1024)  # receiving msg from sender
    msg = msg.decode('utf-8')  # converting into string
    # checking if the msg is valid(i.e detect error using CRC)
    check = checkMsg(msg)
    flag = msg[-1]
    ack = ''
    if check:
        if flag == '0':
            ack = ack0[0:4] + msg[-5:-1]
        else:
            ack = ack1[0:4] + msg[-5:-1]
        s.sendall(bytes(ack, 'utf-8'))  # sending ACK to sender
    else:  # idealy we should never get in this else, since students should send the message correctly
        print('message is encode wrongly')
        time.sleep(to)

    # 2.1  corrupt ACK
    #####################################
    msg = s.recv(1024)
    msg = msg.decode('utf-8')
    check = checkMsg(msg)
    flag = msg[-1]
    ack = ''
    if check:
        if flag == '0':
            ack = ack0[0:4] + msg[-5:-1]
        else:
            ack = ack1[0:4] + msg[-5:-1]
        # courrupting ack
        ack += '1'  # appending '1' will lead to ack being corrupt, test case will be
        # made in such a way that this is guranteed
        s.sendall(bytes(ack, 'utf-8'))
    else:
        print('message is encode wrongly')
        # this will make sender think that, user didn't receive the message
        time.sleep(to)
        # i.e we waited for timeout and didn't send ACK

    # 2.2  since above msg had corrupt ACK, therefore this is response for the resent message form sender
    msg = s.recv(1024)
    msg = msg.decode('utf-8')
    check = checkMsg(msg)
    flag = msg[-1]
    ack = ''
    if check:
        if flag == '0':
            ack = ack0[0:4] + msg[-5:-1]
        else:
            ack = ack1[0:4] + msg[-5:-1]
        s.sendall(bytes(ack, 'utf-8'))
    else:
        print('message is encode wrongly')
        time.sleep(to)

    # 3.1 ACK lost
    #####################################
    msg = s.recv(1024)
    msg = msg.decode('utf-8')
    check = checkMsg(msg)
    flag = msg[-1]
    ack = ''
    if check:
        if flag == '0':
            ack = ack0[0:4] + msg[-5:-1]
        else:
            ack = ack1[0:4] + msg[-5:-1]
        # ack lost then resending ack
        # .5 added so that we can safely assume that the sender has resent
        time.sleep(to+.5)
        # the msg before we try to receive it again
    else:
        print('message is encode wrongly')
        time.sleep(to)

    # 3.2  receiving the resent msg again since previous ACK was lost
    msg = s.recv(1024)
    msg = msg.decode('utf-8')
    check = checkMsg(msg)
    flag = msg[-1]
    ack = ''
    if check:
        if flag == '0':
            ack = ack0[0:4] + msg[-5:-1]
        else:
            ack = ack1[0:4] + msg[-5:-1]
        s.sendall(bytes(ack, 'utf-8'))
    else:
        print('message is encode wrongly')
        time.sleep(to)
    # 4
    #####################################
    msg = s.recv(1024)
    msg = msg.decode('utf-8')
    check = checkMsg(msg)
    flag = msg[-1]
    ack = ''
    if check:
        if flag == '0':
            ack = ack0[0:4] + msg[-5:-1]
        else:
            ack = ack1[0:4] + msg[-5:-1]
        s.sendall(bytes(ack, 'utf-8'))
    else:
        print('message is encode wrongly')
        time.sleep(to)
    # 5
    #####################################
    msg = s.recv(1024)
    msg = msg.decode('utf-8')
    check = checkMsg(msg)
    flag = msg[-1]
    ack = ''
    if check:
        if flag == '0':
            ack = ack0[0:4] + msg[-5:-1]
        else:
            ack = ack1[0:4] + msg[-5:-1]
        s.sendall(bytes(ack, 'utf-8'))
    else:
        print('message is encode wrongly')
        time.sleep(to)

    #####################################
    #####################################
    s.close()


def main():
    # making both functions run on different thread
    t1 = Thread(target=sender, args=[])
    t2 = Thread(target=receiver, args=[])

    t1.start()
    t2.start()

try:
    main() 
except (KeyboardInterrupt, SystemExit):
    Thread.cleanup_stop_thread()
    sys.exit()


